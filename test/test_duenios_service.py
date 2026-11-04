# Tests del service de duenios (C-05, US-201/202/203) contra PostgreSQL real.
# Reciben la sesión como parámetro (DD-02). Cada test resetea la base (seed de reiniciar) y corre
# en un único event loop para no cruzar conexiones asyncpg entre loops.
import asyncio
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from reiniciar import reiniciar  # noqa: E402
from app.modules.duenios import schemas, service  # noqa: E402


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
    """Corre reset + body en un solo event loop (evita cruzar conexiones asyncpg entre loops)."""

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


def test_crear_duenio_devuelve_dto_sin_ficha(url):
    async def body(s):
        dto = await service.crear_duenio(s, schemas.DuenioCreate(nombre="Ana", email="ana@x.com"))
        assert dto.id is not None
        assert dto.nombre == "Ana"
        assert dto.email == "ana@x.com"
        assert dto.ficha is None

    _en_loop(url, body)


def test_crear_duenio_email_duplicado_409(url):
    async def body(s):
        await service.crear_duenio(s, schemas.DuenioCreate(nombre="Ana", email="ana@x.com"))
        with pytest.raises(HTTPException) as exc:
            await service.crear_duenio(s, schemas.DuenioCreate(nombre="Otra", email="ana@x.com"))
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_obtener_duenio_con_ficha(url):
    async def body(s):
        dto = await service.obtener_duenio(s, 1)  # Laura (seed) tiene ficha
        assert dto.ficha is not None
        assert dto.ficha.telefono == "351-1234567"

    _en_loop(url, body)


def test_obtener_duenio_sin_ficha(url):
    async def body(s):
        dto = await service.obtener_duenio(s, 2)  # Carlos (seed) no tiene ficha
        assert dto.ficha is None

    _en_loop(url, body)


def test_obtener_duenio_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.obtener_duenio(s, 9999)
        assert exc.value.status_code == 404

    _en_loop(url, body)


def test_actualizar_duenio_parcial_exclude_unset(url):
    async def body(s):
        # PATCH con sólo `nombre`: el email no debe cambiar (exclude_unset, RN-HTTP-03).
        dto = await service.actualizar_duenio(s, 2, schemas.DuenioUpdate(nombre="Carlos H."))
        assert dto.nombre == "Carlos H."
        assert dto.email == "carlos@example.com"  # sin tocar

    _en_loop(url, body)


def test_actualizar_duenio_email_duplicado_409(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.actualizar_duenio(s, 2, schemas.DuenioUpdate(email="laura@example.com"))
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_actualizar_duenio_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.actualizar_duenio(s, 9999, schemas.DuenioUpdate(nombre="X"))
        assert exc.value.status_code == 404

    _en_loop(url, body)


def test_borrar_duenio_con_mascotas_409(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.borrar_duenio(s, 2)  # Carlos tiene a Lola → RESTRICT
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_borrar_duenio_sin_mascotas_204(url):
    async def body(s):
        nuevo = await service.crear_duenio(s, schemas.DuenioCreate(nombre="Sol", email="sol@x.com"))
        # Sin mascotas ni ficha → el borrado debe completarse sin lanzar excepción (204).
        await service.borrar_duenio(s, nuevo.id)

    _en_loop(url, body)


def test_borrar_duenio_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.borrar_duenio(s, 9999)
        assert exc.value.status_code == 404

    _en_loop(url, body)


def test_crear_ficha_201(url):
    async def body(s):
        dto = await service.crear_ficha(s, 2, schemas.FichaCreate(telefono="123", direccion="Calle 1"))
        assert dto.id is not None
        assert dto.telefono == "123"

    _en_loop(url, body)


def test_crear_ficha_duenio_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.crear_ficha(s, 9999, schemas.FichaCreate(telefono="1", direccion="x"))
        assert exc.value.status_code == 404

    _en_loop(url, body)


def test_crear_ficha_segunda_409(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.crear_ficha(s, 1, schemas.FichaCreate(telefono="1", direccion="x"))  # Laura ya tiene
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_obtener_mascotas_duenio(url):
    async def body(s):
        mascotas = await service.obtener_mascotas_duenio(s, 1)  # Laura: Toby + Mishi
        assert len(mascotas) == 2
        assert {m.nombre for m in mascotas} == {"Toby", "Mishi"}

    _en_loop(url, body)


def test_obtener_mascotas_duenio_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.obtener_mascotas_duenio(s, 9999)
        assert exc.value.status_code == 404

    _en_loop(url, body)
