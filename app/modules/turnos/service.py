# Service del módulo turnos (C-07, US-401): alta con composición M:N en una transacción y borrado.
# Recibe la sesión como parámetro (DD-02). Precio congelado (RN-DS-02) y total calculado en el servidor
# (RN-06); todo-o-nada (RN-TX-01); integridad vía base → IntegrityError → 409 (DD-04).
from decimal import Decimal
from typing import Dict

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos import schemas
from app.modules.turnos.models import Turno, TurnoPractica


def _armar_turno_read(
    turno: Turno, mascota: Mascota, catalogo: Dict[int, Practica], ids: list[int]
) -> schemas.TurnoRead:
    practicas = [
        schemas.PracticaTurnoRead(
            practica_id=pid,
            nombre=catalogo[pid].nombre,
            precio_unitario=catalogo[pid].precio,
        )
        for pid in ids
    ]
    return schemas.TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=schemas.MascotaResumen(id=mascota.id, nombre=mascota.nombre, especie=mascota.especie),
        practicas=practicas,
    )


async def crear_turno(session: AsyncSession, payload: schemas.TurnoCreate) -> schemas.TurnoRead:
    """US-401: alta de turno con prácticas anidadas, en UNA transacción (RN-TX-01).

    Trae los precios del catálogo, copia cada uno a precio_unitario (freeze, RN-DS-02) y calcula el
    total en el servidor (RN-06). Práctica inexistente → 409 sin guardar nada; duplicada → PK
    compuesta → 409 (RN-07); mascota inexistente → 409.
    """
    # 1. Mascota (necesaria para la respuesta embebida; la FK además la garantiza).
    mascota = await session.get(Mascota, payload.mascota_id)
    if mascota is None:
        raise HTTPException(status_code=409, detail="La mascota no existe")

    # 2. Prácticas del catálogo (precios a congelar + nombres para la respuesta).
    ids = [p.practica_id for p in payload.practicas]
    practicas = (await session.scalars(select(Practica).where(Practica.id.in_(set(ids))))).all()
    catalogo = {p.id: p for p in practicas}
    faltantes = [pid for pid in set(ids) if pid not in catalogo]
    if faltantes:
        raise HTTPException(status_code=409, detail="Una o más prácticas no existen")

    # 3. Turno con total calculado por el servidor (RN-06).
    total = sum((catalogo[pid].precio for pid in ids), Decimal("0.00"))
    turno = Turno(mascota_id=mascota.id, fecha=payload.fecha, motivo=payload.motivo, total=total)
    session.add(turno)
    try:
        await session.flush()  # asigna turno.id (la FK a mascota ya fue validada)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="La mascota no existe")

    # 4. turno_practica con el precio copiado del catálogo (freeze, RN-DS-02).
    for pid in ids:
        session.add(
            TurnoPractica(turno_id=turno.id, practica_id=pid, precio_unitario=catalogo[pid].precio)
        )

    # 5. Commit en UNA transacción (RN-TX-01); práctica duplicada → PK compuesta → 409 (RN-07).
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Una práctica está duplicada en el turno")

    # Recargar para normalizar fecha a UTC (el ejemplo de la consigna: 10:30-03:00 → 13:30Z).
    await session.refresh(turno)
    return _armar_turno_read(turno, mascota, catalogo, ids)


async def borrar_turno(session: AsyncSession, turno_id: int) -> None:
    """US-401 / Flujo 10: borrado del turno; la base borra sus turno_practica por ON DELETE CASCADE
    (RN-09); el ORM no las toca (passive_deletes, RN-INT-02). 404 si no existe."""
    turno = await session.get(Turno, turno_id)
    if turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    await session.delete(turno)
    await session.commit()


def _turno_a_dto(turno: Turno) -> schemas.TurnoRead:
    """Arma el TurnoRead a partir de un turno con relaciones precargadas (mascota y prácticas)."""
    practicas = [
        schemas.PracticaTurnoRead(
            practica_id=tp.practica_id,
            nombre=tp.practica.nombre,
            precio_unitario=tp.precio_unitario,
        )
        for tp in turno.practicas
    ]
    return schemas.TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=schemas.MascotaResumen(
            id=turno.mascota.id, nombre=turno.mascota.nombre, especie=turno.mascota.especie
        ),
        practicas=practicas,
    )


async def obtener_turno(session: AsyncSession, turno_id: int) -> schemas.TurnoRead:
    """US-501 CA-2 / Flujo 9: detalle del turno con mascota y prácticas en un número FIJO de consultas
    (2): joinedload a uno (mascota) + selectinload para la colección (prácticas→práctica). No crece
    con la cantidad de prácticas y no depende de lazy load (RN-REL-03)."""
    turno = await session.scalar(
        select(Turno)
        .options(
            joinedload(Turno.mascota),
            selectinload(Turno.practicas).joinedload(TurnoPractica.practica),
        )
        .where(Turno.id == turno_id)
    )
    if turno is None:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    return _turno_a_dto(turno)
