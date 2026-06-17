from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.pdf_router import router as pdf
from app.routers.pricelist_router import router as pricelist
from app.routers.quotation_router import router as quotation
from app.routers.tipo_de_cambio_router import router as tipo_de_cambio

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf)

app.include_router(pricelist)

app.include_router(quotation)

app.include_router(tipo_de_cambio)