from datetime import datetime
from app.core.exceptions import ValidationError # Asumiendo una excepción del core

class AssetLoanService:
    def checkout(self, asset_id, borrower_id, due_at, note=""):
        asset = self.db.query("asset").get(asset_id)
        if asset.status != 'available':
            raise ValidationError("El activo no está disponible.")

        loan_data = {
            "asset_id": asset_id,
            "borrower_user_id": borrower_id,
            "checkout_at": datetime.now(),
            "due_at": due_at,
            "status": "open",
            "checkout_note": note
        }
        loan = self.create(loan_data)

        asset.status = 'loaned'
        self.db.save(asset)
        return loan

    def return_asset(self, loan_id, note=""):
        loan = self.get(loan_id)
        if loan.status != 'open':
            raise ValidationError("Este préstamo ya no está activo.")
        
        loan.returned_at = datetime.now()
        loan.status = 'returned'
        loan.return_note = note

        asset = self.db.query("asset").get(loan.asset_id)
        asset.status = 'available'
        
        self.db.save(loan)
        self.db.save(asset)

    def mark_maintenance(self, asset_id, note=""):
        asset = self.db.query("asset").get(asset_id)
        asset.status = 'maintenance'
        asset.notes = note
        self.db.save(asset)

    def release_maintenance(self, asset_id: int):
        asset = self.db.query("asset").get(asset_id)
        
        if not asset:
            raise ValidationError("El recurso no existe.")
            
        if asset.status != 'maintenance':
            raise ValidationError("El recurso no está en mantenimiento.")

        asset.status = 'available'
        self.db.save(asset)
        return True