# reiniciar.py — borrado de tablas, SQLModel.metadata.create_all y seed de datos de ejemplo.
# US-302 (C-04): deja la base en un estado conocido y funciona sobre una base vacía (DD-03: sin Alembic).
# Ejecutar: `python reiniciar.py` (lee DATABASE_URL del entorno/.env vía app.core.config).
import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlmodel import SQLModel

from app.core import config  # noqa: F401 — valida fail-fast DATABASE_URL
from app.core.database import create_engine, create_sessionmaker
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica


async def _cargar_seed(session) -> None:
    """Seed mínimo obligatorio (US-302 CA-2), con precios coherentes con el caso C-06."""
    # 2 dueños (uno con ficha).
    laura = Duenio(nombre="Laura Pérez", email="laura@example.com")
    carlos = Duenio(nombre="Carlos Gómez", email="carlos@example.com")
    session.add(laura)
    session.add(carlos)
    await session.flush()  # asigna ids autoincrementales

    session.add(
        FichaDuenio(duenio_id=laura.id, telefono="351-1234567", direccion="Av. Siempre Viva 742")
    )

    # 3 mascotas.
    toby = Mascota(nombre="Toby", especie="perro", duenio_id=laura.id)
    mishi = Mascota(nombre="Mishi", especie="gato", duenio_id=laura.id)
    lola = Mascota(nombre="Lola", especie="conejo", duenio_id=carlos.id)
    session.add(toby)
    session.add(mishi)
    session.add(lola)
    await session.flush()

    # 4 prácticas (Consulta y Vacuna antirrábica reproducen el ejemplo de POST /turnos/).
    consulta = Practica(nombre="Consulta", precio=Decimal("15000.00"))
    desparasitacion = Practica(nombre="Desparasitación", precio=Decimal("8000.00"))
    vacuna = Practica(nombre="Vacuna antirrábica", precio=Decimal("12000.00"))
    corte = Practica(nombre="Corte de uñas", precio=Decimal("5000.00"))
    session.add(consulta)
    session.add(desparasitacion)
    session.add(vacuna)
    session.add(corte)
    await session.flush()

    # 1 turno con 2 prácticas (total = 15000 + 12000 = 27000, RN-06).
    turno = Turno(
        mascota_id=toby.id,
        fecha=datetime(2026, 11, 12, 13, 30, tzinfo=timezone.utc),
        motivo="Control anual",
        total=Decimal("27000.00"),
    )
    session.add(turno)
    await session.flush()
    session.add(
        TurnoPractica(turno_id=turno.id, practica_id=consulta.id, precio_unitario=Decimal("15000.00"))
    )
    session.add(
        TurnoPractica(turno_id=turno.id, practica_id=vacuna.id, precio_unitario=Decimal("12000.00"))
    )


async def reiniciar(engine) -> None:
    """Borra las tablas, las crea con create_all y carga el seed (US-302, DD-03)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with create_sessionmaker(engine)() as session:
        await _cargar_seed(session)
        await session.commit()


async def main() -> None:
    engine = create_engine()
    try:
        await reiniciar(engine)
    finally:
        await engine.dispose()
    print("Base reiniciada: esquema creado y seed cargado (2 dueños, 3 mascotas, 4 prácticas, 1 turno).")


if __name__ == "__main__":
    asyncio.run(main())
