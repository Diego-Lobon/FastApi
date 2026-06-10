import pdfplumber
import re

def extract_products(pdf_path: str):

    products = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                match = re.search(
                    r'^\s*\d+\s+(\d{8,20}).*?S/\s+\d+\.\d+\s+(\d+)\s+IGV',
                    line
                )

                if match:

                    codigo = match.group(1)

                    cantidad = int(match.group(2))

                    products.append({
                        "codigo": codigo,
                        "cantidad": cantidad
                    })

    return products

