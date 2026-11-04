# Service del módulo mascotas (C-06, US-204): alta, listado paginado y detalle con precarga.
# Recibe la sesión como parámetro (DD-02). Integridad vía base: FK violada → IntegrityError → 409 (DD-04).
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.mascotas import schemas
from app.modules.mascotas.models import Mascota


async def crear_mascota(session: AsyncSession, payload: schemas.MascotaCreate) -> schemas.MascotaRead:
    """US-204 CA-1: alta de mascota; dueño inexistente → FK violada → IntegrityError → 409 (C-04)."""
    mascota = Mascota(nombre=payload.nombre, especie=payload.especie, duenio_id=payload.duenio_id)
    session.add(mascota)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="El dueño no existe")
    # Recién creada: no se accede a la relación para evitar lazy load (duenio=None).
    return schemas.MascotaRead(
        id=mascota.id, nombre=mascota.nombre, especie=mascota.especie, duenio_id=mascota.duenio_id
    )


async def listar_mascotas(session: AsyncSession, page: int, size: int) -> schemas.MascotaPage:
    """US-204 CA-2 / RN-HTTP-04: envoltorio {items,total,page,size,pages}; page>pages → 422 (IN-01);
    la primera página siempre responde aunque no haya resultados (pages mínimo 1)."""
    total = await session.scalar(select(func.count()).select_from(Mascota))
    pages = max(1, (total + size - 1) // size)
    if page > pages:
        raise HTTPException(status_code=422, detail="Página fuera de rango")

    mascotas = (
        await session.scalars(
            select(Mascota).order_by(Mascota.id).offset((page - 1) * size).limit(size)
        )
    ).all()
    items = [
        schemas.MascotaRead(id=m.id, nombre=m.nombre, especie=m.especie, duenio_id=m.duenio_id)
        for m in mascotas
    ]
    return schemas.MascotaPage(items=items, total=total, page=page, size=size, pages=pages)


async def obtener_mascota(session: AsyncSession, mascota_id: int) -> schemas.MascotaRead:
    """US-204 CA-3: detalle de la mascota con su dueño (joinedload a uno, RN-REL-03); 404 si no existe."""
    mascota = await session.scalar(
        select(Mascota).options(joinedload(Mascota.duenio)).where(Mascota.id == mascota_id)
    )
    if mascota is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")

    duenio = None
    if mascota.duenio is not None:
        duenio = schemas.DuenioResumen(
            id=mascota.duenio.id, nombre=mascota.duenio.nombre, email=mascota.duenio.email
        )
    return schemas.MascotaRead(
        id=mascota.id,
        nombre=mascota.nombre,
        especie=mascota.especie,
        duenio_id=mascota.duenio_id,
        duenio=duenio,
    )
