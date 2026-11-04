# Service del módulo duenios (C-05): lógica + traducción de errores + lecturas con precarga.
# Recibe la sesión como parámetro (DD-02). Integridad vía base: IntegrityError → 409 (DD-04, RN-INT-01).
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.duenios import schemas
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota


def _ficha_a_dto(ficha: Optional[FichaDuenio]) -> Optional[schemas.FichaRead]:
    if ficha is None:
        return None
    return schemas.FichaRead(id=ficha.id, telefono=ficha.telefono, direccion=ficha.direccion)


def _duenio_a_dto(duenio: Duenio) -> schemas.DuenioRead:
    return schemas.DuenioRead(
        id=duenio.id,
        nombre=duenio.nombre,
        email=duenio.email,
        ficha=_ficha_a_dto(duenio.ficha),
    )


async def crear_duenio(session: AsyncSession, payload: schemas.DuenioCreate) -> schemas.DuenioRead:
    """US-201: alta de dueño; email repetido → 409 atrapando IntegrityError (RN-01, RN-INT-01)."""
    duenio = Duenio(nombre=payload.nombre, email=payload.email)
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    # Dueño recién creado: todavía no tiene ficha (no se accede a la relación para evitar lazy load).
    return schemas.DuenioRead(id=duenio.id, nombre=duenio.nombre, email=duenio.email, ficha=None)


async def obtener_duenio(session: AsyncSession, duenio_id: int) -> schemas.DuenioRead:
    """US-202 CA-1: detalle del dueño con su ficha precargada (joinedload a uno, RN-REL-03)."""
    duenio = await session.scalar(
        select(Duenio).options(joinedload(Duenio.ficha)).where(Duenio.id == duenio_id)
    )
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return _duenio_a_dto(duenio)


async def actualizar_duenio(
    session: AsyncSession, duenio_id: int, payload: schemas.DuenioUpdate
) -> schemas.DuenioRead:
    """US-202 CA-2: PATCH parcial con exclude_unset (RN-HTTP-03); 404/409."""
    duenio = await session.scalar(
        select(Duenio).options(joinedload(Duenio.ficha)).where(Duenio.id == duenio_id)
    )
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(duenio, campo, valor)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    return _duenio_a_dto(duenio)


async def borrar_duenio(session: AsyncSession, duenio_id: int) -> None:
    """US-202 CA-3: borrado; 409 si tiene mascotas (FK RESTRICT, RN-08); 404 si no existe."""
    duenio = await session.get(Duenio, duenio_id)
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    await session.delete(duenio)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="No se puede borrar: el dueño tiene mascotas")


async def crear_ficha(
    session: AsyncSession, duenio_id: int, payload: schemas.FichaCreate
) -> schemas.FichaRead:
    """US-203 CA-1: alta de ficha (1:1); 404 dueño inexistente; 409 segunda ficha (RN-03, UNIQUE)."""
    duenio = await session.get(Duenio, duenio_id)
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    ficha = FichaDuenio(duenio_id=duenio_id, telefono=payload.telefono, direccion=payload.direccion)
    session.add(ficha)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El dueño ya tiene una ficha")
    return schemas.FichaRead(id=ficha.id, telefono=ficha.telefono, direccion=ficha.direccion)


async def obtener_mascotas_duenio(session: AsyncSession, duenio_id: int) -> List[schemas.MascotaRead]:
    """GET /duenios/{id}/mascotas: mascotas del dueño con selectinload (colección, RN-REL-03)."""
    duenio = await session.scalar(
        select(Duenio).options(selectinload(Duenio.mascotas)).where(Duenio.id == duenio_id)
    )
    if duenio is None:
        raise HTTPException(status_code=404, detail="Dueño no encontrado")
    return [
        schemas.MascotaRead(id=m.id, nombre=m.nombre, especie=m.especie) for m in duenio.mascotas
    ]
