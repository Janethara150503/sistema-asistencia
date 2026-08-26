"""
Cliente centralizado de Convex para toda la app Flet.
Cualquier pantalla que necesite hablar con el backend importa
`client` desde aqui, en vez de crear su propia conexion.
"""
import os
from dotenv import load_dotenv
from convex import ConvexClient

load_dotenv()

CONVEX_URL = os.environ.get("CONVEX_URL")

if not CONVEX_URL:
    raise RuntimeError(
        "CONVEX_URL no esta configurado. Revisa el archivo .env en frontend/"
    )

client = ConvexClient(CONVEX_URL)
