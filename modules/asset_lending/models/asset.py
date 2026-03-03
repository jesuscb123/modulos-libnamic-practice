from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field

class Asset(Base):
    __tablename__ = "asset_lending_asset"
    __abstract__ = False
    __model__ = "asset"
    __service__ = "modules.asset_lending.services.asset_loan_service.AssetService"

    name = field(String(180), required=True, public=True)
    asset_code = field(String(50), required=True, public=True, info={"label": {"es": "Código", "en": "Code"}})
    status = field(
        String(20), 
        default="available", 
        info={
            "choices": [
                {"label": "Disponible", "value": "available"},
                {"label": "Prestado", "value": "loaned"},
                {"label": "Mantenimiento", "value": "maintenance"}
            ]
        }
    )
    location_id = field(Integer, ForeignKey("asset_lending_location.id"), required=True)
    location = relationship("AssetLocation", foreign_keys=lambda: [Asset.location_id])
    
    responsible_user_id = field(UUID, ForeignKey("core_user.id"), required=True)
    responsible_user = relationship("User", foreign_keys=lambda: [Asset.responsible_user_id])
    
    notes = field(Text, required=False, public=True)