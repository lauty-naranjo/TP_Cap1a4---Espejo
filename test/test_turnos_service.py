# Tests del service de turnos (C-07, US-401) contra PostgreSQL real.
# Patrón igual a los demás tests de service: base reseteada con el seed y un event loop por test.
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from reiniciar import reiniciar  # noqa: E402
from app.modules.turnos import schemas, service  # noqa: E402
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


def _turno_ejemplo():
    """Reproduce el contrato exacto de la consigna (mascota 1, prácticas 1 y 3)."""
    return schemas.TurnoCreate(
        mascota_id=1,
        fecha=datetime(2026, 11, 12, 10, 30, tzinfo=timezone(timedelta(hours=-3))),
        motivo="Control anual",
        practicas=[schemas.PracticaTurnoCreate(practica_id=1), schemas.PracticaTurnoCreate(practica_id=3)],
    )


def test_crear_turno_valido_con_precios_congelados(url):
    async def body(s):
        dto = await service.crear_turno(s, _turno_ejemplo())

        assert dto.total == Decimal("27000.00")  # 15000 + 12000
        assert dto.motivo == "Control anual"
        assert dto.mascota.id == 1
        assert dto.mascota.nombre == "Toby"

        # fecha normalizada a UTC: 10:30-03:00 == 13:30Z (SU-03).
        utc = dto.fecha.astimezone(timezone.utc)
        assert utc.hour == 13 and utc.minute == 30

        # prácticas con precio copiado del catálogo (RN-06, RN-DS-02).
        por_id = {p.practica_id: p for p in dto.practicas}
        assert set(por_id) == {1, 3}
        assert por_id[1].nombre == "Consulta"
        assert por_id[1].precio_unitario == Decimal("15000.00")
        assert por_id[3].nombre == "Vacuna antirrábica"
        assert por_id[3].precio_unitario == Decimal("12000.00")

    _en_loop(url, body)


def test_crear_turno_practica_inexistente_409_y_no_guarda_nada(url):
    async def body(s):
        payload = schemas.TurnoCreate(
            mascota_id=1,
            fecha=datetime(2026, 11, 12, 10, 30, tzinfo=timezone.utc),
            motivo="X",
            practicas=[schemas.PracticaTurnoCreate(practica_id=1), schemas.PracticaTurnoCreate(practica_id=9999)],
        )
        with pytest.raises(HTTPException) as exc:
            await service.crear_turno(s, payload)
        assert exc.value.status_code == 409

        # todo-o-nada (RN-TX-01): el seed trae 1 turno y sigue habiendo 1.
        total = await s.scalar(select(func.count()).select_from(Turno))
        assert total == 1

    _en_loop(url, body)


def test_crear_turno_practica_duplicada_409(url):
    async def body(s):
        payload = schemas.TurnoCreate(
            mascota_id=1,
            fecha=datetime(2026, 11, 12, 10, 30, tzinfo=timezone.utc),
            motivo="X",
            practicas=[schemas.PracticaTurnoCreate(practica_id=1), schemas.PracticaTurnoCreate(practica_id=1)],
        )
        with pytest.raises(HTTPException) as exc:
            await service.crear_turno(s, payload)
        assert exc.value.status_code == 409  # RN-07: PK compuesta rechaza el duplicado

    _en_loop(url, body)


def test_crear_turno_mascota_inexistente_409(url):
    async def body(s):
        payload = schemas.TurnoCreate(
            mascota_id=9999,
            fecha=datetime(2026, 11, 12, 10, 30, tzinfo=timezone.utc),
            motivo="X",
            practicas=[schemas.PracticaTurnoCreate(practica_id=1)],
        )
        with pytest.raises(HTTPException) as exc:
            await service.crear_turno(s, payload)
        assert exc.value.status_code == 409

    _en_loop(url, body)


def test_crear_turno_lista_vacia_rechazada_por_dto():
    # RN-05: al menos una práctica → 422 en el contrato (min_length=1).
    with pytest.raises(ValidationError):
        schemas.TurnoCreate(
            mascota_id=1,
            fecha=datetime(2026, 11, 12, 10, 30, tzinfo=timezone.utc),
            motivo="X",
            practicas=[],
        )


def test_borrar_turno_204_y_sus_practicas_desaparecen(url):
    async def body(s):
        # Seed: turno id=1 con 2 prácticas.
        await service.borrar_turno(s, 1)

        turno = await s.get(Turno, 1)
        assert turno is None
        # RN-09: la base borró las turno_practica por CASCADE.
        restantes = await s.scalar(
            select(func.count()).select_from(TurnoPractica).where(TurnoPractica.turno_id == 1)
        )
        assert restantes == 0

    _en_loop(url, body)


def test_borrar_turno_inexistente_404(url):
    async def body(s):
        with pytest.raises(HTTPException) as exc:
            await service.borrar_turno(s, 9999)
        assert exc.value.status_code == 404

    _en_loop(url, body)
