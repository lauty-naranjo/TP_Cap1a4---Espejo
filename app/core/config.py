# Configuración por entorno (US-103): la ÚNICA configuración leída del entorno es DATABASE_URL.
# Sin DATABASE_URL (ni en .env ni en el entorno) el proceso debe abortar con error claro (fail-fast).
# La validación corre al importarse este módulo (que app.main importa), garantizando que
# uvicorn aborta el arranque ANTES de levantarse (design D2).
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no definida — copiar env.example a .env")
