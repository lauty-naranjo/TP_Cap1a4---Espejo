# Test de reiniciar.py (C-04, US-302): corre el script real sobre la base y verifica el seed.
# CA-1 (funciona sobre base vacía) + CA-2 (seed mínimo: 2 dueños/1 ficha, 3 mascotas, 4 prácticas,
# 1 turno con 2 prácticas) y precios coherentes con el caso C-06.
#
# Lee DATABASE_URL directo de .env (no del config global, que otros tests pueden pisar con
# credenciales placeholder vía os.environ.setdefault) y lo inyecta al subprocess y al engine propio.
import asyncio
import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import func, select

from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

REPO_ROOT = Path(__file__).resolve().parent.parent


def _database_url_real():
    """DATABASE_URL leído directamente del .env del repo (ignora os.environ para no heredar placeholders)."""
    for linea in (REPO_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea.startswith("DATABASE_URL="):
            return linea.split("=", 1)[1].strip()
    raise RuntimeError("No se encontró DATABASE_URL en .env (copiar env.example a .env)")


def _correr_reiniciar(url):
    env = {**os.environ, "DATABASE_URL": url}
    return subprocess.run(
        [sys.executable, "reiniciar.py"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )


async def _verificar_seed(url):
    engine = create_async_engine(url)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with sessionmaker() as s:
            n_duenios = await s.scalar(select(func.count()).select_from(Duenio))
            n_fichas = await s.scalar(select(func.count()).select_from(FichaDuenio))
            n_mascotas = await s.scalar(select(func.count()).select_from(Mascota))
            n_practicas = await s.scalar(select(func.count()).select_from(Practica))
            n_turnos = await s.scalar(select(func.count()).select_from(Turno))
            n_tp = await s.scalar(select(func.count()).select_from(TurnoPractica))

            assert n_duenios == 2
            assert n_fichas == 1
            assert n_mascotas == 3
            assert n_practicas == 4
            assert n_turnos == 1
            assert n_tp == 2

            # Precios coherentes con el contrato del ejemplo de POST /turnos/ (C-06).
            consulta = await s.scalar(select(Practica).where(Practica.nombre == "Consulta"))
            vacuna = await s.scalar(select(Practica).where(Practica.nombre == "Vacuna antirrábica"))
            assert str(consulta.precio) == "15000.00"
            assert str(vacuna.precio) == "12000.00"

            turno = await s.scalar(select(Turno))
            assert str(turno.total) == "27000.00"
    finally:
        await engine.dispose()


def test_reiniciar_funciona_sobre_base_y_carga_seed():
    url = _database_url_real()
    resultado = _correr_reiniciar(url)
    assert resultado.returncode == 0, f"reiniciar.py falló:\n{resultado.stderr}"
    asyncio.run(_verificar_seed(url))
