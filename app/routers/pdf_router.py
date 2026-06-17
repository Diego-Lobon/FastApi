from fastapi import APIRouter,UploadFile,File
from app.services.pdf_service import extract_products
import shutil
import os

router=APIRouter()


@router.post("/validate-pdf")
async def validate_pdf(
    pdf:UploadFile=File(...)
):

    os.makedirs(
        "app/uploads",
        exist_ok=True
    )

    path=f"app/uploads/{pdf.filename}"

    with open(path,"wb") as f:

        shutil.copyfileobj(
            pdf.file,
            f
        )

    return extract_products(path)