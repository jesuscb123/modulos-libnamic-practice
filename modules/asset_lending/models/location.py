from __future__ import annotations
from sqlalchemy import Boolean, String
from app.core.base import Base
from app.core.fields import field

class AssetLocation(Base):
    __tablename__ = "asset_lending_location"
    __abstract__ = False
    __model__ = "location"
    __service__ = "modules.asset_lending.services.asset_loan_service.AssetLocationService"

    __selector_config__ = {
        "label_field": "name",
        "search_fields": ["name", "code"],
        "columns": [
            {"field": "name", "label": "Nombre"},
            {"field": "code", "label": "Código"},
            {"field": "is_active", "label": "Activo"},
        ],
    }

    name = field(String(100), required=True, public=True, info={"label": {"es": "Ubicación", "en": "Location"}})
    code = field(String(20), required=True, public=True, info={"label": {"es": "Código", "en": "Code"}})
    is_active = field(Boolean, default=True, public=True, info={"label": {"es": "Activo", "en": "Active"}})