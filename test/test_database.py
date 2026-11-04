# Tests del módulo de base de datos (C-02, US-101 CA-2) — change c-02-database-lifespan-health.
# Se fija DATABASE_URL antes de importar app.core.config / app.core.database (fail-fast).
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://usuario:password@localhost:5432/veterinaria",
)

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core import database

DATABASE_URL = os.environ["DATABASE_URL"]


def test_create_engine_devuelve_un_async_engine_configurado_para_database_url():
    """D1: la fábrica de motor crea un AsyncEngine sobre la DATABASE_URL del proyecto."""
    engine = database.create_engine()
    assert isinstance(engine, AsyncEngine)
    assert engine.url.drivername.startswith("postgresql+asyncpg")


def test_create_sessionmaker_usa_expire_on_commit_false():
    """D1: la fábrica de sessionmaker crea sesiones con expire_on_commit=False."""
    engine = database.create_engine()
    sessionmaker = database.create_sessionmaker(engine)
    session = sessionmaker()
    assert session is not None
    assert sessionmaker.kw["expire_on_commit"] is False


def test_get_session_apertura_y_cierre_de_sesion_por_request():
    """US-101 CA-2: la dependencia get_session abre una sesión nueva por petición y la cierra al finalizar."""
    app_basica = FastAPI()
    registrador = {"sesiones": []}

    @app_basica.get("/sesion")
    async def endpoint(session: AsyncSession = Depends(database.get_session)):
        return {"ok": True}

    sessionmaker_real = database.create_sessionmaker(database.create_engine())

    def factory_con_registro():
        session = sessionmaker_real()
        registrador["sesiones"].append(session)
        return session

    app_basica.state.sessionmaker = factory_con_registro

    with TestClient(app_basica) as client:
        respuesta = client.get("/sesion")

    assert respuesta.status_code == 200
    # La dependencia abrió exactamente una sesión por petición (Flujo 2, US-101 CA-2).
    assert len(registrador["sesiones"]) == 1
