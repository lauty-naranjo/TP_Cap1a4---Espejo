# Motor asíncrono + fábrica de sesiones (C-02, US-101 CA-1/CA-2; diseño D1/D2/D5).
# La única configuración del proyecto es DATABASE_URL (validada fail-fast en app.core.config).
# `SQL_ECHO=true` activa el log de sentencias SQL (evidencia del caso C-07, sin afectar el default).
import os
from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core import config


def create_engine() -> AsyncEngine:
    """Fábrica del motor async a partir de la única variable de configuración (DATABASE_URL, diseño D5).

    `SQL_ECHO=true` habilita `echo` (log de SQL) para capturar la evidencia de consultas fijas del
    caso C-07; apagado por defecto.
    """
    echo = os.getenv("SQL_ECHO", "").strip().lower() in ("1", "true", "yes", "on")
    return create_async_engine(str(config.DATABASE_URL), echo=echo)



def create_sessionmaker(engine: AsyncEngine):
    """Fábrica de sesiones async con expire_on_commit=False (diseño D1, RN de expiración de estado)."""
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependencia async con yield: una sesión nueva por petición (Flujo 2, US-101 CA-2).

    Abre la sesión desde el sessionmaker del app.state (creado en el lifespan) y la cierra
    al finalizar la petición (commit/rollback lo hace el service dentro de esta sesión).
    """
    session: AsyncSession = request.app.state.sessionmaker()
    try:
        yield session
    finally:
        await session.close()
