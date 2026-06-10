import xmlrpc.client


def create_quotation(data):

    url = "https://intirepo-cisur-staging-32459294.dev.odoo.com/"
    db = "intirepo-cisur-staging-32459294"
    username = "miramar@isur.com.pe"
    password = "1234567u"

    common = xmlrpc.client.ServerProxy(
        f"{url}/xmlrpc/2/common"
    )

    uid = common.authenticate(
        db,
        username,
        password,
        {}
    )

    if not uid:
        raise Exception("No se pudo autenticar")

    models = xmlrpc.client.ServerProxy(
        f"{url}/xmlrpc/2/object"
    )

    # CLIENTE
    cliente = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [[("name", "=", data["cliente"])]],
        {
            "fields": ["id"],
            "limit": 1
        }
    )

    if not cliente:
        raise Exception(
            f'Cliente no encontrado: {data["cliente"]}'
        )

    partner_id = cliente[0]["id"]

    # LISTA DE PRECIOS
    pricelist = models.execute_kw(
        db,
        uid,
        password,
        "product.pricelist",
        "search_read",
        [[("name", "=", data["listaPrecio"])]],
        {
            "fields": ["id"],
            "limit": 1
        }
    )

    pricelist_id = pricelist[0]["id"]

    # TERMINO PAGO
    payment_map = {
        "Pago inmediato": "Inmediato",
        "15 días": "15 días",
        "21 días": "21 días",
        "30 días": "30 días",
        "45 días": "45 días",
    }

    payment_name = payment_map.get(
        data["terminoPago"]
    )

    payment_term = models.execute_kw(
        db,
        uid,
        password,
        "account.payment.term",
        "search_read",
        [[("name", "=", payment_name)]],
        {
            "fields": ["id"],
            "limit": 1
        }
    )

    payment_term_id = (
        payment_term[0]["id"]
        if payment_term
        else False
    )

    # PRODUCTOS
    order_lines = []

    for item in data["products"]:

        producto = models.execute_kw(
            db,
            uid,
            password,
            "product.product",
            "search_read",
            [[("default_code", "=", item["codigo"])]],
            {
                "fields": ["id"],
                "limit": 1
            }
        )

        if not producto:
            continue

        order_lines.append(
            (
                0,
                0,
                {
                    "product_id": producto[0]["id"],
                    "product_uom_qty": item["cantidad"]
                }
            )
        )

    sale_order_id = models.execute_kw(
        db,
        uid,
        password,
        "sale.order",
        "create",
        [{
            "partner_id": partner_id,
            "payment_term_id": payment_term_id,
            "pricelist_id": pricelist_id,
            "note": data["observacion"],
            "order_line": order_lines
        }]
    )

    cotizacion = models.execute_kw(
        db,
        uid,
        password,
        "sale.order",
        "read",
        [[sale_order_id]],
        {
            "fields": ["name"]
        }
    )

    return {
        "success": True,
        "sale_order_id": sale_order_id,
        "numero": cotizacion[0]["name"]
    }