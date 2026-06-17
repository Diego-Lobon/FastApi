from typing import Optional
from fastapi import APIRouter, HTTPException
from app.services.quotation_service import buscar_clientes, create_quotation


router = APIRouter()


@router.post("/create-quotation")
async def quotation(data: dict):

    try:
        return create_quotation(data)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@router.get("/clientes")
async def clientes(
    search: Optional[str] = ""
):
    return buscar_clientes(search)