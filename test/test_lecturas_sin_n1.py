# Tests de lecturas sin N+1 (C-08, US-501) — change c-08-lecturas-sin-n1.
# Verifican que los detalles con relaciones se resuelven con un número FIJO de consultas SQL,
# independiente de la cantidad de filas relacionadas (RN-REL-03). El conteo usa un listener
# SQLAlchemy `before_cursor_execute` sobre el engine.
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from reiniciar import reiniciar  # noqa: E402
from app.modules.duenios import service as duenios_service  # noqa: E402
from app.modules.turnos import schemas as turnos_schemas  # noqa: E402
from app.modules.turnos import service as turnos_service  # noqa: E402


def _database_url_real():
    for linea in (REPO_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("DATABASE_URL="):
            return linea.split("=", 1)[1].strip()
    raise RuntimeError("Sin DATABASE_URL en .env")


@pytest.fixture
def url():
    return _database_url_real()


def _en_loop_contando(url, fn):
    """Reset + body con un contador de sentencias SQL (antes de cada cursor execute)."""

    async def wrapper():
        engine = create_async_engine(url)
        contador = {"n": 0}

        def _contar(conn, cursor, statement, parameters, context, executemany):
            contador["n"] += 1

        event.listen(engine.sync_engine, "before_cursor_execute", _contar)
        try:
            await reiniciar(engine)
            sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
            async with sessionmaker() as s:
                await fn(s, contador)
        finally:
            await engine.dispose()

    asyncio.run(wrapper())


def _turno(practica_ids, motivo="X"):
    return turnos_schemas.TurnoCreate(
        mascota_id=1,
        fecha=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        motivo=motivo,
        practicas=[turnos_schemas.PracticaTurnoCreate(practica_id=pid) for pid in practica_ids],
    )


def test_obtener_turno_misma_cantidad_consultas_con_1_y_3_practicas(url):
    """US-501 CA-2 / caso C-07: el detalle del turno emite 2 consultas fijas (joinedload + selectinload)
    tanto con 1 como con 3 prácticas: no crece con la cantidad de prácticas."""

    async def body(s, contador):
        t1 = await turnos_service.crear_turno(s, _turno([1]))
        t3 = await turnos_service.crear_turno(s, _turno([1, 2, 3]))

        contador["n"] = 0
        dto1 = await turnos_service.obtener_turno(s, t1.id)
        q1 = contador["n"]

        contador["n"] = 0
        dto3 = await turnos_service.obtener_turno(s, t3.id)
        q3 = contador["n"]

        assert len(dto1.practicas) == 1
        assert len(dto3.practicas) == 3
        assert q1 == q3, f"consultas con 1 práctica ({q1}) != con 3 ({q3})"
        assert q1 == 2, f"se esperaban 2 consultas fijas, se emitieron {q1}"

    _en_loop_contando(url, body)


def test_obtener_duenio_con_ficha_consulta_fija(url):
    """US-501 CA-3: el detalle del dueño con su ficha se resuelve con 1 consulta (joinedload a uno)."""

    async def body(s, contador):
        contador["n"] = 0
        dto = await duenios_service.obtener_duenio(s, 1)  # Laura (seed) tiene ficha
        q = contador["n"]

        assert dto.ficha is not None
        assert q == 1, f"el detalle de dueño debe emitir 1 consulta, emitió {q}"

    _en_loop_contando(url, body)
