from fastapi import APIRouter

from app.schemas.pricelist_schema import (
    ListaPreciosSchema
)

from app.services.pricelist_service import (
    crear_lista_precios_odoo,
    obtener_listas_precios,
    eliminar_lista_precio,
    obtener_lista_por_id,
    actualizar_lista_precio
)


router = APIRouter(
    prefix="/api/v1/pricelists",
    tags=["Pricelists"]
)


# ==================
# LISTAR
# ==================

@router.get("")
async def listar_listas():

    return obtener_listas_precios()


# ==================
# CREAR
# ==================

@router.post("")
async def crear_lista(
    payload: ListaPreciosSchema
):

    id_lista = crear_lista_precios_odoo(
        payload.model_dump()
    )

    return {
        "id": id_lista
    }

@router.delete("/{id_lista}")
async def eliminar(
    id_lista: int
):

    return eliminar_lista_precio(
        id_lista
    )

@router.get("/{id_lista}")
async def obtener(
    id_lista:int
):

    return obtener_lista_por_id(
        id_lista
    )

@router.put("/{id_lista}")
async def actualizar(
    id_lista: int,
    payload: ListaPreciosSchema
):

    return actualizar_lista_precio(
        id_lista,
        payload.model_dump()
    )