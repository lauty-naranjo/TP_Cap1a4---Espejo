# Tests del módulo practicas (C-06, US-205) contra PostgreSQL real + validación de DTO (RN-04).
import asyncio
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from reiniciar import reiniciar  # noqa: E402
from app.modules.practicas import schemas, service  # noqa: E402


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


def test_crear_practica_devuelve_dto(url):
    async def body(s):
        dto = await service.crear_practica(
            s, schemas.PracticaCreate(nombre="Ecografía", precio=Decimal("20000.00"))
        )
        assert dto.id is not None
        assert dto.nombre == "Ecografía"
        assert dto.precio == Decimal("20000.00")

    _en_loop(url, body)


def test_crear_practica_nombre_duplicado_409(url):
    async def body(s):
        # "Consulta" ya existe en el seed → UNIQUE rechaza → 409 (RN-02, RN-INT-01).
        with pytest.raises(HTTPException) as exc:
            await service.crear_practica(
                s, schemas.PracticaCreate(nombre="Consulta", precio=Decimal("1.00"))
            )
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_practica_precio_no_positivo_rechazado_por_dto():
    # RN-04: el DTO exige precio > 0 → 422 en el contrato (sin llegar a la base).
    with pytest.raises(ValidationError):
        schemas.PracticaCreate(nombre="X", precio=Decimal("0"))
    with pytest.raises(ValidationError):
        schemas.PracticaCreate(nombre="X", precio=Decimal("-5.00"))


def test_listar_practicas_catalogo_completo(url):
    async def body(s):
        # Seed: 4 prácticas.
        practicas = await service.listar_practicas(s)
        assert len(practicas) == 4
        assert {p.nombre for p in practicas} >= {"Consulta", "Desparasitación", "Vacuna antirrábica", "Corte de uñas"}

    _en_loop(url, body)
