from app.core.odoo_client import connect_odoo
from app.core.config import DB, PASSWORD

def actualizar_precios_odoo(productos_frontend):
    uid, models = connect_odoo()
    
    productos_actualizados = 0
    productos_no_encontrados = []

    # LOG: Para ver qué estructura exacta está mandando Angular
    print("\n=== INICIANDO SINCRONIZACIÓN DESDE FRONTEND ===")
    print(f"Total de productos recibidos: {len(productos_frontend)}")
    print(f"Muestra del primer producto recibido: {productos_frontend[0] if productos_frontend else 'Ninguno'}")

    for item in productos_frontend:
        # Obtenemos el código y le quitamos espacios fantasmas con .strip() si existe
        print(item)
        codigo_crudo = item.get("codigo") or item.get("default_code")
        codigo = str(codigo_crudo).strip() if codigo_crudo is not None else None
        
        if not codigo or codigo == "None" or codigo == "":
            print("⚠️ Saltando un producto porque el 'codigo' llegó vacío o no existe en el JSON.")
            continue

        costo_soles = float(item.get("costo_soles") or 0)
        precio_venta_soles = float(item.get("precio_venta_soles") or 0)

        print(f"\n🔍 Buscando en Odoo código: '{codigo}' | Costo local: {costo_soles} | Venta local: {precio_venta_soles}")

        # 1. Buscar el ID del producto en Odoo usando la Referencia Interna
        odoo_product = models.execute_kw(
            DB,
            uid,
            PASSWORD,
            "product.product",
            "search_read",
            [[("default_code", "=", codigo)]],
            {"fields": ["id", "name", "default_code"], "limit": 1},
        )

        if odoo_product:
            product_id = odoo_product[0]["id"]
            nombre_odoo = odoo_product[0].get("name", "Desconocido")
            print(f"✅ ¡Encontrado en Odoo! ID: {product_id} - Nombre: {nombre_odoo}")
            
            # 2. Escribir los nuevos valores en Odoo
            models.execute_kw(
                DB,
                uid,
                PASSWORD,
                "product.product",
                "write",
                [[product_id], {
                    "standard_price": costo_soles,
                    "list_price": precio_venta_soles
                }]
            )
            print(f"💾 Precios actualizados con éxito en Odoo para '{codigo}'.")
            productos_actualizados += 1
        else:
            print(f"❌ No se encontró ningún producto en Odoo con default_code == '{codigo}'")
            productos_no_encontrados.append(codigo)

    print("\n=== FIN DE LA SINCRONIZACIÓN ===")
    print(f"Actualizados: {productos_actualizados} | No encontrados: {len(productos_no_encontrados)}\n")

    return {
        "status": "success",
        "message": f"Se actualizaron {productos_actualizados} productos en Odoo exitosamente.",
        "no_encontrados": productos_no_encontrados
    }