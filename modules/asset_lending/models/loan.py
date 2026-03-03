from __future__ import annotations
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UUID
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.fields import field

class AssetLoan(Base):
    __tablename__ = "asset_lending_loan"
    __abstract__ = False
    __model__ = "loan"
    __service__ = "modules.asset_lending.services.asset_loan_service.AssetLoanService"

    asset_id = field(Integer, ForeignKey("asset_lending_asset.id"), required=True)
    asset = relationship("Asset", foreign_keys=lambda: [AssetLoan.asset_id])
    
    borrower_user_id = field(UUID, ForeignKey("core_user.id"), required=True)
    borrower_user = relationship("User", foreign_keys=lambda: [AssetLoan.borrower_user_id])
    
    checkout_at = field(DateTime(timezone=True), required=True)
    due_at = field(DateTime(timezone=True), required=True)
    returned_at = field(DateTime(timezone=True), required=False)
    
    status = field(String(20), default="open", info={
        "choices": [
            {"label": "Abierto", "value": "open"},
            {"label": "Devuelto", "value": "returned"},
            {"label": "Vencido", "value": "overdue"}
        ]
    })
    checkout_note = field(Text)
    return_note = field(Text)