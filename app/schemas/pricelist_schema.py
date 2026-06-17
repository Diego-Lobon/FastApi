from pydantic import BaseModel
from typing import Literal


class ProductoItemSchema(BaseModel):

    id:int|str

    codigo:str

    nombre:str

    precioEditable:float

    descuentoEditable:float

    tipoRegla:Literal[
        "DESCUENTO",
        "PRECIO_FIJO"
    ]


class ListaPreciosSchema(BaseModel):

    nombre:str

    moneda:Literal[
        "PEN",
        "USD"
    ]

    productos:list[
        ProductoItemSchema
    ]