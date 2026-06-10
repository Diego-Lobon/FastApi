from fastapi import FastAPI, UploadFile, File
from services.pdf_service import extract_products
from services.odoo_service import get_stock_by_product
from fastapi.middleware.cors import CORSMiddleware
from services.quotation import create_quotation

import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/validate-pdf")
async def validate_pdf(
    pdf: UploadFile = File(...)
):

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    file_path = f"uploads/{pdf.filename}"

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            pdf.file,
            buffer
        )

    products = extract_products(
        file_path
    )

    result = []

    for product in products:

        stock = get_stock_by_product(
            product
        )

        result.append(stock)

    return {
        "codes_found": len(products),
        "products": result
    }

@app.post("/create-quotation")
async def create_quotation_endpoint(
    data: dict
):
    return create_quotation(data)