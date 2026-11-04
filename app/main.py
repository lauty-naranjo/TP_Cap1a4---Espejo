# App mínima arrancable (C-01): FastAPI sin routers, lifespan vacío.
# La configuración se valida acá al importarse → fail-fast de DATABASE_URL (US-103).
# C-02 completa el lifespan real (motor SQLModel/asyncpg + sessionmaker) y registra el
# router de health. Routers de dominio: C-05+.
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import config  # noqa: F401 — importa con validación fail-fast de DATABASE_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Vacío por decisión de diseño (D4): sin motor ni sessionmaker acá.
    # C-02 crea/cierra el motor async dentro de este hook.
    yield


app = FastAPI(lifespan=lifespan)
