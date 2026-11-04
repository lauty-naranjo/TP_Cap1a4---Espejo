# Service del módulo practicas (C-06, US-205): alta y catálogo completo.
# Recibe la sesión como parámetro (DD-02). Nombre repetido → IntegrityError → 409 (RN-02, RN-INT-01).
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.practicas import schemas
from app.modules.practicas.models import Practica


async def crear_practica(session: AsyncSession, payload: schemas.PracticaCreate) -> schemas.PracticaRead:
    """US-205 CA-1: alta de práctica; nombre repetido → 409 atrapando IntegrityError (RN-02).
    El precio ≤ 0 no llega acá: lo rechaza el DTO con 422 (RN-04)."""
    practica = Practica(nombre=payload.nombre, precio=payload.precio)
    session.add(practica)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El nombre de la práctica ya existe")
    return schemas.PracticaRead(id=practica.id, nombre=practica.nombre, precio=practica.precio)


async def listar_practicas(session: AsyncSession) -> list[schemas.PracticaRead]:
    """US-205 CA-2 / SU-06: catálogo completo como lista simple (sin envoltorio de paginación)."""
    practicas = (await session.scalars(select(Practica).order_by(Practica.id))).all()
    return [
        schemas.PracticaRead(id=p.id, nombre=p.nombre, precio=p.precio) for p in practicas
    ]
