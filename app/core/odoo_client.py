import ssl
import xmlrpc.client

from app.core.config import *

ssl_context = ssl._create_unverified_context()


def connect_odoo():

    common = xmlrpc.client.ServerProxy(
        f"{URL}/xmlrpc/2/common",
        context=ssl_context
    )

    uid = common.authenticate(
        DB,
        USERNAME,
        PASSWORD,
        {}
    )

    models = xmlrpc.client.ServerProxy(
        f"{URL}/xmlrpc/2/object",
        context=ssl_context
    )

    return uid, models