# App mínima arrancable (C-01 + C-02): FastAPI con lifespan que crea el motor async + sessionmaker.
# La configuración se valida al importarse → fail-fast de DATABASE_URL (US-103).
# C-02 completa el lifespan real (motor SQLModel/asyncpg + sessionmaker) y registra el
# router de health. Routers de dominio: C-05+.
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import config  # noqa: F401 — importa con validación fail-fast de DATABASE_URL
from app.core.database import create_engine, create_sessionmaker
from app.modules.health.router import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Motor + sessionmaker creados al arrancar (C-02, diseño D2) y guardados en app.state;
    # al apagar se cierra el motor liberando el pool (US-101 CA-1).
    engine = create_engine()
    sessionmaker = create_sessionmaker(engine)
    app.state.engine = engine
    app.state.sessionmaker = sessionmaker
    app.include_router(health_router)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
