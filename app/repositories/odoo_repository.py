from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD


def search_product(code):

    uid, models = connect_odoo()

    return models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.product",
        "search_read",
        [[("default_code", "=", code)]],
    )