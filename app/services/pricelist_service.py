from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD

def crear_lista_precios_odoo(datos_lista):
    uid, models = connect_odoo()

    # CORREGIDO: Angular ya envía 'PEN' o 'USD' de forma directa
    moneda = datos_lista["moneda"]

    currency = models.execute_kw(
        DB, uid, PASSWORD,
        "res.currency",
        "search",
        [[("name", "=", moneda)]],
        {"limit": 1}
    )

    if not currency:
        raise Exception(f"Moneda '{moneda}' no encontrada en Odoo")

    item_ids = []

    for p in datos_lista["productos"]:
        product = models.execute_kw(
            DB, uid, PASSWORD,
            "product.product",
            "search",
            [[("default_code", "=", p["codigo"])]]
        )

        if not product:
            continue

        regla = {
            "product_id": product[0],
            "applied_on": "0_product_variant",
            "min_quantity": 1
        }

        if p["tipoRegla"] == "PRECIO_FIJO":
            regla["compute_price"] = "fixed"
            regla["fixed_price"] = p["precioEditable"]
        else:
            regla["compute_price"] = "percentage"
            regla["percent_price"] = p["descuentoEditable"]

        item_ids.append((0, 0, regla))

    return models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "create",
        [{
            "name": datos_lista["nombre"],
            "currency_id": currency[0],
            "item_ids": item_ids
        }]
    )

def obtener_listas_precios():
    uid, models = connect_odoo()
    listas = models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "search_read",
        [[]],
        {"fields": ["id", "name"]}
    )
    return listas

def eliminar_lista_precio(id_lista: int):
    uid, models = connect_odoo()
    existe = models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "search",
        [[("id", "=", id_lista)]]
    )

    if not existe:
        raise Exception("Lista de precios no encontrada")

    models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "unlink",
        [[id_lista]]
    )

    return {"message": "Lista eliminada"}

def obtener_lista_por_id(id_lista):
    uid, models = connect_odoo()
    lista = models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "read",
        [[id_lista]],
        {"fields": ["id", "name", "currency_id", "item_ids"]}
    )

    if not lista:
        raise Exception("Lista no encontrada")

    reglas = models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist.item",
        "search_read",
        [[("id", "in", lista[0]["item_ids"])]],
        {"fields": ["product_id", "fixed_price", "percent_price", "compute_price"]}
    )

    productos = []

    for r in reglas:
        if not r["product_id"]:
            continue

        producto = models.execute_kw(
            DB, uid, PASSWORD,
            "product.product",
            "read",
            [[r["product_id"][0]]],
            {"fields": ["default_code", "name"]}
        )

        if not producto:
            continue

        producto = producto[0]

        productos.append({
            "id": r["product_id"][0],
            "codigo": producto.get("default_code", ""),
            "name": producto.get("name", ""),
            "precioEditable": r.get("fixed_price", 0),
            "descuentoEditable": r.get("percent_price", 0),
            "tipoRegla": "PRECIO_FIJO" if r["compute_price"] == "fixed" else "DESCUENTO"
        })

    # CORREGIDO: Retornamos 'PEN' o 'USD' directamente tal como viene de Odoo lista[0]["currency_id"][1]
    return {
        "id": lista[0]["id"],
        "nombre": lista[0]["name"],
        "moneda": lista[0]["currency_id"][1],
        "productos": productos
    }

def actualizar_lista_precio(id_lista, datos_lista):
    uid, models = connect_odoo()
    existe = models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "search",
        [[("id", "=", id_lista)]]
    )

    if not existe:
        raise Exception("Lista de precios no encontrada")

    # CORREGIDO: Usamos directamente la moneda sin traducción manual
    moneda = datos_lista["moneda"]

    currency = models.execute_kw(
        DB, uid, PASSWORD,
        "res.currency",
        "search",
        [[("name", "=", moneda)]],
        {"limit": 1}
    )

    if not currency:
        raise Exception(f"Moneda '{moneda}' no encontrada en Odoo")

    item_ids = []

    for p in datos_lista["productos"]:
        product = models.execute_kw(
            DB, uid, PASSWORD,
            "product.product",
            "search",
            [[("default_code", "=", p["codigo"])]],
            {"limit": 1}
        )

        if not product:
            continue

        regla = {
            "product_id": product[0],
            "applied_on": "0_product_variant",
            "min_quantity": 1
        }

        if p["tipoRegla"] == "PRECIO_FIJO":
            regla["compute_price"] = "fixed"
            regla["fixed_price"] = p["precioEditable"]
        else:
            regla["compute_price"] = "percentage"
            regla["percent_price"] = p["descuentoEditable"]

        item_ids.append((0, 0, regla))

    models.execute_kw(
        DB, uid, PASSWORD,
        "product.pricelist",
        "write",
        [
            [id_lista],
            {
                "name": datos_lista["nombre"],
                "currency_id": currency[0],
                "item_ids": [
                    (5, 0, 0),
                    *item_ids
                ]
            }
        ]
    )

    return {"message": "Lista actualizada"}