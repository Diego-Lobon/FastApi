from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD


def create_quotation(data):

    uid, models = connect_odoo()

    # ===================
    # CLIENTE
    # ===================

    cliente = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [[("name", "=", data["cliente"])]],
        {
            "fields": ["id"],
            "limit": 1
        },
    )

    if not cliente:
        raise Exception(
            f'Cliente no encontrado: {data["cliente"]}'
        )

    partner_id = cliente[0]["id"]

    # ===================
    # LISTA PRECIOS
    # ===================

    pricelist = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "product.pricelist",
        "search_read",
        [[("name", "=", data["listaPrecio"])]],
        {
            "fields": ["id"],
            "limit": 1
        },
    )

    if not pricelist:
        raise Exception(
            "Lista de precios no encontrada"
        )

    pricelist_id = pricelist[0]["id"]

    # ===================
    # TERMINO PAGO
    # ===================

    payment_term_id = False
    
    # Validamos que nos llegue el término de pago desde el frontend
    if data.get("terminoPago"):
        # Como mandamos el ID numérico desde Angular, buscamos directamente por ID en Odoo
        payment_term = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "account.payment.term",
            "search_read",
            [[("id", "=", int(data["terminoPago"]))]], # 💡 Cambiado a buscar por ID directo
            {
                "fields": ["id"],
                "limit": 1,
            },
        )

        if payment_term:
            payment_term_id = payment_term[0]["id"]
        else:
            print(f"Advertencia: No se encontró el Payment Term con ID {data['terminoPago']} en Odoo.")

    # ===================
    # PRODUCTOS
    # ===================

    order_lines = []

    for item in data["products"]:

        producto = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.product",
            "search_read",
            [[
                (
                    "default_code",
                    "=",
                    item["codigo"]
                )
            ]],
            {
                "fields": [
                    "id",
                    "name",
                    "qty_available"
                ],
                "limit": 1,
            },
        )

        if not producto:
            raise Exception(
                f'Producto no encontrado: {item["codigo"]}'
            )

        # 💡 SOLUCIÓN: Usar .get() con un valor por defecto de 1 si "cantidad" no viene en el JSON
        cantidad_solicitada = item.get("cantidad", 1)

        order_lines.append(
            (
                0,
                0,
                {
                    "product_id": producto[0]["id"],
                    "product_uom_qty": cantidad_solicitada,
                },
            )
        )

    # ===================
    # CREAR COTIZACION
    # ===================

    sale_order_id = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "sale.order",
        "create",
        [
            {
                "partner_id": partner_id,
                "payment_term_id": payment_term_id,
                "pricelist_id": pricelist_id,
                "note": data["observacion"],
                "order_line": order_lines,
            }
        ],
    )

    cotizacion = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "sale.order",
        "read",
        [[sale_order_id]],
        {
            "fields": ["name"]
        },
    )

    return {
        "id": sale_order_id,
        "cotizacion": cotizacion[0]["name"]
    }

def buscar_clientes(search=""):

    uid, models = connect_odoo()

    domain = [
        (
            "customer_rank",
            ">",
            0
        )
    ]

    # Solo filtrar si escribieron algo
    if search.strip():
        domain.append(
            (
                "name",
                "ilike",
                search
            )
        )

    clientes = models.execute_kw(
        DB,
        uid,
        PASSWORD,
        "res.partner",
        "search_read",
        [domain],
        {
            "fields": ["name"],

            # si search vacío traer más
            "limit": 1000 if not search else 10,

            "order": "name asc"
        }
    )

    return {
        "clientes": [
            c["name"]
            for c in clientes
        ]
    }