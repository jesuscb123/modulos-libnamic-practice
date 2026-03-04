import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from modules.feedback_moderation.models.feedback import Suggestion
from modules.feedback_moderation.services.feedback import SuggestionService

@pytest.fixture
def mock_service():
    """Crea una instancia del servicio con una base de datos simulada (Mock)"""
    # Engañamos al __init__ del BaseService
    service = SuggestionService(MagicMock())
    # Simulamos el repositorio y la sesión de SQLAlchemy
    service.repo = MagicMock()
    service.repo.session = MagicMock()
    return service

@patch("app.core.base.BaseService.create")
def test_initial_state_is_pending_and_private(mock_super_create, mock_service):
    """Prueba que la creación inyecta 'pending' e 'is_public=False' pase lo que pase."""
    # Le decimos al mock que, cuando intente guardar, simplemente devuelva el diccionario
    mock_super_create.side_effect = lambda x: x
    

    payload = {
        "title": "Añadir modo oscuro",
        "content": "Sería genial para la vista.",
        "is_public": True  # ¡Ataque!
    }
    
    result = mock_service.create(payload)
    
    # Comprobamos que nuestro interceptor machacó la inyección
    assert result["status"] == "pending", "Debe forzar el estado a pending"
    assert result["is_public"] is False, "Debe forzar la privacidad a False"
    mock_super_create.assert_called_once()

@patch("modules.feedback_moderation.services.feedback.get_current_user_id")
@patch("modules.feedback_moderation.services.feedback.serialize")
def test_publish_transition_makes_it_public(mock_serialize, mock_get_user, mock_service):
    """Prueba la transición a publicada."""
    # Simulamos al usuario logueado
    mock_get_user.return_value = "uuid-del-moderador"

    fake_suggestion = Suggestion(id=1, status="pending", is_public=False)
    mock_service.repo.session.get.return_value = fake_suggestion
    
    mock_serialize.side_effect = lambda obj: {"status": obj.status, "is_public": obj.is_public, "moderation_note": obj.moderation_note}
    
    result = mock_service.publish(id=1, note="Aprobado por moderación")
    
    assert result["status"] == "published"
    assert result["is_public"] is True
    assert result["moderation_note"] == "Aprobado por moderación"
    mock_service.repo.session.commit.assert_called_once()

@patch("modules.feedback_moderation.services.feedback.get_current_user_id")
@patch("modules.feedback_moderation.services.feedback.serialize")
def test_reject_transition_keeps_it_private(mock_serialize, mock_get_user, mock_service):
    """Prueba la transición a rechazada."""
    mock_get_user.return_value = "uuid-del-moderador"
    fake_suggestion = Suggestion(id=2, status="pending", is_public=False)
    mock_service.repo.session.get.return_value = fake_suggestion
    mock_serialize.side_effect = lambda obj: {"status": obj.status, "is_public": obj.is_public, "moderation_note": obj.moderation_note}
    
    result = mock_service.reject(id=2, note="No es viable")
    
    assert result["status"] == "rejected"
    assert result["is_public"] is False
    assert result["moderation_note"] == "No es viable"
    mock_service.repo.session.commit.assert_called_once()

def test_merge_fails_if_target_is_same_as_source(mock_service):
    """Prueba la validación de negocio: no se puede fusionar un ticket consigo mismo."""
    with pytest.raises(HTTPException) as exc_info:
        mock_service.merge(id=5, target_id=5, note="Merge loop")
        
    assert exc_info.value.status_code == 400
    assert "No puedes fusionar consigo misma" in exc_info.value.detail