# Tests del service de mascotas (C-06, US-204) contra PostgreSQL real.
# Patrón igual a test_duenios_service.py: sesión por test, base reseteada con el seed de reiniciar
# y un único event loop por test (evita cruzar conexiones asyncpg entre loops).
import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from reiniciar import reiniciar  # noqa: E402
from app.modules.mascotas import schemas, service  # noqa: E402
from app.modules.mascotas.models import Mascota  # noqa: E402
from app.modules.turnos.models import Turno, TurnoPractica  # noqa: E402


def _database_url_real():
    for linea in (REPO_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("DATABASE_URL="):
            return linea.split("=", 1)[1].strip()
    raise RuntimeError("Sin DATABASE_URL en .env")


@pytest.fixture
def url():
    return _database_url_real()


def _en_loop(url, fn):
    async def wrapper():
        engine = create_async_engine(url)
        try:
            await reiniciar(engine)
            sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
            async with sessionmaker() as s:
                await fn(s)
        finally:
            await engine.dispose()

    asyncio.run(wrapper())


def test_crear_mascota_devuelve_dto(url):
    async def body(s):
        dto = await service.crear_mascota(
            s, schemas.MascotaCreate(nombre="Nina", especie="perro", duenio_id=1)
        )
        assert dto.id is not None
        assert dto.nombre == "Nina"
        assert dto.especie == "perro"
        assert dto.duenio_id == 1
        assert dto.duenio is None  # el alta no embebe el dueño (evita lazy load)

    _en_loop(url, body)


def test_crear_mascota_duenio_inexistente_409(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.crear_mascota(
                s, schemas.MascotaCreate(nombre="X", especie="gato", duenio_id=9999)
            )
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_listar_mascotas_paginado(url):
    async def body(s):
        # Seed: 3 mascotas. size=2 → total=3, pages=2.
        dto = await service.listar_mascotas(s, page=1, size=2)
        assert dto.total == 3
        assert dto.pages == 2
        assert dto.page == 1
        assert dto.size == 2
        assert len(dto.items) == 2

        dto2 = await service.listar_mascotas(s, page=2, size=2)
        assert len(dto2.items) == 1

    _en_loop(url, body)


def test_listar_mascotas_page_fuera_de_rango_422(url):
    async def body(s):
        # total=3, size=2 → pages=2; page=3 está fuera de rango (IN-01).
        with pytest.raises(HTTPException) as exc:
            await service.listar_mascotas(s, page=3, size=2)
        assert exc.value.status_code == 422

    _en_loop(url, body)


def test_listar_mascotas_primera_pagina_responde_aunque_este_vacia(url):
    async def body(s):
        # Vaciar mascotas (en orden de dependencias) y verificar que page=1 responde igual.
        await s.execute(delete(TurnoPractica))
        await s.execute(delete(Turno))
        await s.execute(delete(Mascota))
        await s.commit()

        dto = await service.listar_mascotas(s, page=1, size=20)
        assert dto.total == 0
        assert dto.pages == 1
        assert dto.items == []

    _en_loop(url, body)


def test_obtener_mascota_con_duenio(url):
    async def body(s):
        dto = await service.obtener_mascota(s, 1)  # Toby (seed), dueño Laura (id=1)
        assert dto.nombre == "Toby"
        assert dto.duenio is not None
        assert dto.duenio.nombre == "Laura Pérez"
        assert dto.duenio.email == "laura@example.com"

    _en_loop(url, body)


def test_obtener_mascota_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.obtener_mascota(s, 9999)
        assert exc.value.status_code == 404

    _en_loop(url, body)
