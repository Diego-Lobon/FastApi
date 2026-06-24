import pdfplumber
import re

from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD


def extract_products(pdf_path):
    uid, models = connect_odoo()
    products = []
    id_precio_lista = None
    item_blocks = []

    all_text = ""
    all_lines = []

    # ==========================================
    # 1. EXTRAER TEXTO GENERAL
    # ==========================================
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += text + "\n"
                all_lines.extend(text.split("\n"))
                
    print("--- INICIO TEXTO COMPLETO DEL PDF ---")
    print(all_text)
    print("--- FIN TEXTO COMPLETO DEL PDF ---")

    # Extraer ID: COT-8457-08 -> 8
    match_id = re.search(r"COT-\d+-(\d+)", all_text, re.IGNORECASE)
    if match_id:
        id_precio_lista = int(match_id.group(1))
        print("ID EXTRAIDO:", id_precio_lista)

    # ==========================================
    # 2. EXTRAER CÓDIGOS DE PRODUCTO Y CANTIDADES
    # ==========================================
    for line in all_lines:
        line_clean = line.strip()
        
        if not line_clean:
            continue

        # REGEX MODIFICADO: 
        # 1. ^(\d{1,3})\s+            -> Item inicial (ej: 04)
        # 2. ([A-Za-z0-9\-]{5,15})    -> Código alfa-numérico con guiones (ej: 10022087-1)
        # 3. \s+(.+?)\s+              -> Descripción (búsqueda no ambiciosa)
        # 4. (\d+)\s+(?:\$|S\/)       -> Cantidad seguida de un símbolo de precio ($ o S/)
        match_producto = re.match(r"^(\d{1,3})\s+([A-Za-z0-9\-]{5,15})\s+(.+?)\s+(\d+)\s+(?:\$|S\/)", line_clean)
        
        if match_producto:
            codigo_detectado = match_producto.group(2)
            cantidad_detectada = int(match_producto.group(4))
            
            print(f"-> [LOG] Línea coincide con producto. Código: {codigo_detectado} | Cantidad: {cantidad_detectada}")
            
            item_blocks.append({
                "codigo": codigo_detectado,
                "cantidad": cantidad_detectada
            })
        else:
            # Plan de contingencia si la descripción es muy larga y deforma el final de la línea
            match_auxiliar = re.match(r"^(\d{1,3})\s+([A-Za-z0-9\-]{5,15})\s+", line_clean)
            if match_auxiliar and not line_clean.startswith("Op. Gravada"):
                codigo_detectado = match_auxiliar.group(2)
                
                # Intentamos rescatar la cantidad buscando el número previo al precio
                buscar_cantidad = re.search(r"\s+(\d+)\s+(?:\$|S\/)", line_clean)
                cantidad_detectada = int(buscar_cantidad.group(1)) if buscar_cantidad else 1
                
                print(f"-> [LOG RECOV] Rescatado -> Código: {codigo_detectado} | Cantidad: {cantidad_detectada}")
                
                item_blocks.append({
                    "codigo": codigo_detectado,
                    "cantidad": cantidad_detectada
                })

    print("\n==================================")
    print("TOTAL DE ITEMS EXTRAIDOS INTERNAMENTE:", item_blocks)
    print("==================================\n")

    # ==========================================
    # 3. CONSULTAR STOCK ODOO
    # ==========================================
    for item in item_blocks:
        codigo = item["codigo"]
        cantidad = item["cantidad"]

        print(f"BUSCANDO EN ODOO CÓDIGO: {codigo}")

        producto = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.product",
            "search_read",
            [[("default_code", "=", codigo)]],
            {
                "fields": ["name", "qty_available"],
                "limit": 1,
            },
        )

        if producto:
            stock = producto[0]["qty_available"]
            print(f"✅ ¡Encontrado en Odoo! {producto[0]['name']} - Stock: {stock}")
            products.append({
                "codigo": codigo,
                "nombre": producto[0]["name"],
                "cantidad": cantidad,
                "stock_libre": stock,
                "disponible": (stock >= cantidad),
            })
        else:
            print(f"⚠️ Código {codigo} no existe en Odoo.")
            products.append({
                "codigo": codigo,
                "nombre": f"No encontrado ({codigo})",
                "cantidad": cantidad,
                "stock_libre": 0,
                "disponible": False,
            })

    return {
        "codes_found": len(products),
        "products": products,
        "id_precio_lista": id_precio_lista,
    }