from fastapi import APIRouter, HTTPException
from app.services.tipo_de_cambio_service import actualizar_precios_odoo # Ajusta la ruta de importación si es necesario

router = APIRouter()

@router.post("/sync-prices")
async def sync_prices(data: dict):
    try:
        # data["products"] contendrá la lista filtrada enviada desde Angular
        productos = data.get("products", [])
        if not productos:
            raise Exception("No se proporcionaron productos para actualizar.")
            
        return actualizar_precios_odoo(productos)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )