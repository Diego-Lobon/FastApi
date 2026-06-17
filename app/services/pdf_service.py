import pdfplumber
import re

from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD


def extract_products(pdf_path):

    uid, models = connect_odoo()

    products = []

    # NUEVO
    id_precio_lista = None

    # ==========================
    # EXTRAER TEXTO DEL PDF
    # ==========================

    all_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            text = page.extract_text()

            if text:

                lines = text.split("\n")

                all_lines.extend(lines)

    # ==========================
    # EXTRAER ID
    # Busca:
    # ID: 8
    # ==========================

    for line in all_lines:

        line_str = line.strip()

        match_id = re.search(
            r"\bID\s*:\s*(\d+)\b",
            line_str,
            re.IGNORECASE,
        )

        if match_id:

            id_precio_lista = int(
                match_id.group(1)
            )

            print("ID EXTRAIDO:", id_precio_lista)

            break

    # ==========================
    # AGRUPAR ITEMS
    # ==========================

    item_blocks = []
    current_block = []
    dentro_de_tabla = False

    for line in all_lines:

        line_str = line.strip()

        if not line_str:
            continue

        if (
            "Precio Unit" in line
            or "Descripcion" in line
        ):
            dentro_de_tabla = True
            continue

        if (
            "Sub Total" in line
            or "Subtotal" in line
            or "Gracias por su preferencia" in line
        ):

            dentro_de_tabla = False

            if current_block:
                item_blocks.append(current_block)

                current_block = []

            continue

        if dentro_de_tabla:

            es_nuevo_item = re.match(
                r"^\s*\d+\s+",
                line
            )

            if es_nuevo_item:

                if current_block:
                    item_blocks.append(
                        current_block
                    )

                current_block = [line_str]

            else:

                if current_block:
                    current_block.append(
                        line_str
                    )

    if current_block:
        item_blocks.append(current_block)

    # ==========================
    # PROCESAR ITEMS
    # ==========================

    for block in item_blocks:

        lineas = block.copy()

        if (
            len(lineas) > 1
            and re.match(r"^-\w+", lineas[1])
        ):

            sufijo = re.match(
                r"^(-[\w]+)",
                lineas[1]
            ).group(1)

            lineas[0] = re.sub(
                r"^(\d+\s+[\w]+)",
                lambda m: m.group(1) + sufijo,
                lineas[0],
            )

            lineas[1] = re.sub(
                r"^-\w+\s*",
                "",
                lineas[1],
            )

        full_text = " ".join(lineas)

        print("ITEM:", full_text)

        match = re.search(
            r"^\d+\s+([\w\-]+).*?(?:\$|S/)\s+\d+\.\d+\s+(\d+)\s+IGV",
            full_text
        )

        if not match:
            continue

        codigo = match.group(1)

        cantidad = int(
            match.group(2)
        )

        producto = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.product",
            "search_read",
            [
                [
                    (
                        "default_code",
                        "=",
                        codigo
                    )
                ]
            ],
            {
                "fields": [
                    "name",
                    "qty_available"
                ],
                "limit": 1
            }
        )

        if producto:

            stock = producto[0]["qty_available"]

            products.append({
                "codigo": codigo,
                "nombre": producto[0]["name"],
                "cantidad": cantidad,
                "stock_libre": stock,
                "disponible": stock >= cantidad
            })

        else:

            products.append({
                "codigo": codigo,
                "nombre": f"No encontrado ({codigo})",
                "cantidad": cantidad,
                "stock_libre": 0,
                "disponible": False
            })

    return {
        "codes_found": len(products),
        "products": products,

        # NUEVO
        "id_precio_lista": id_precio_lista
    }