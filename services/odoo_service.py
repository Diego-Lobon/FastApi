import xmlrpc.client

URL = "https://intirepo-cisur-staging-32459294.dev.odoo.com"
DB = "intirepo-cisur-staging-32459294"
USERNAME = "miramar@isur.com.pe"
PASSWORD = "1234567u"


def connect_odoo():

    common = xmlrpc.client.ServerProxy(
        f"{URL}/xmlrpc/2/common"
    )

    uid = common.authenticate(
        DB,
        USERNAME,
        PASSWORD,
        {}
    )

    if not uid:
        raise Exception("Error autenticando")

    models = xmlrpc.client.ServerProxy(
        f"{URL}/xmlrpc/2/object"
    )

    return uid, models


def get_stock_by_product(product):

    uid, models = connect_odoo()

    codigo = product["codigo"]

    cantidad = product["cantidad"]

    product_ids = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.product",
        "search",
        [[("default_code", "=", codigo)]]
    )

    if not product_ids:
        return {
            "codigo": codigo,
            "cantidad": cantidad,
            "encontrado": False
        }

    product_odoo = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.product",
        "read",
        [product_ids],
        {
            "fields": [
                "name",
                "qty_available",
                "free_qty",
                "virtual_available"
            ]
        }
    )[0]

    return {
        "codigo": codigo,
        "cantidad": cantidad,
        "encontrado": True,
        "nombre": product_odoo["name"],
        "stock_fisico": product_odoo["qty_available"],
        "stock_libre": product_odoo["free_qty"],
        "stock_pronosticado": product_odoo["virtual_available"],
    }