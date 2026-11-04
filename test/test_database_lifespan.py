# Tests del lifespan de la aplicación (C-02, US-101 CA-1) — change c-02-database-lifespan-health.
# Se fija DATABASE_URL antes de importar app.main (config.py la lee al importarse; fail-fast).
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://usuario:password@localhost:5432/veterinaria",
)

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from app.main import app

DATABASE_URL = os.environ["DATABASE_URL"]


def test_lifespan_crea_engine_y_sessionmaker_en_app_state():
    """US-101 CA-1: con DATABASE_URL presente, el lifespan crea motor+sessionmaker en app.state."""
    with TestClient(app) as client:
        assert app.state.engine is not None
        assert app.state.sessionmaker is not None
        assert isinstance(app.state.engine, AsyncEngine)
        sessionmaker = app.state.sessionmaker
        session = sessionmaker()
        assert session is not None
        assert str(app.state.engine.url.drivername).startswith("postgresql+asyncpg")


def test_lifespan_cierra_el_motor_al_salir_del_contexto():
    """US-101 CA-1: al salir del contexto del lifespan se cierra el motor (engine.dispose)."""
    engine_mock = MagicMock()
    engine_mock.dispose = AsyncMock()
    sessionmaker_mock = MagicMock()

    with (
        patch("app.main.create_engine", return_value=engine_mock) as mock_engine_factory,
        patch("app.main.create_sessionmaker", return_value=sessionmaker_mock) as mock_sessionmaker_factory,
    ):
        with TestClient(app) as client:
            pass
        mock_engine_factory.assert_called_once()
        mock_sessionmaker_factory.assert_called_once_with(engine_mock)
        engine_mock.dispose.assert_awaited_once()


def test_lifespan_registra_routers_en_startup():
    """US-101 CA-1 / diseño D3: el lifespan registra los routers de la app (health) al arrancar."""
    with patch.object(app, "include_router") as mock_include_router:
        with TestClient(app) as client:
            pass
        mock_include_router.assert_called_once()
