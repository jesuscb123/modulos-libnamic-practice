from .models.location import AssetLocation
from .models.asset import Asset
from .models.loan import AssetLoan

# Esto permite que el ORM/CLI encuentre los modelos al escanear el paquete
__all__ = ["AssetLocation", "Asset", "AssetLoan"]