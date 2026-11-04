# Router del módulo mascotas (C-06, US-204): rutas HTTP — reciben, delegan y declaran la respuesta.
# Códigos de la consigna (RN-HTTP-01): 201 al crear, 404/409/422. El 422 de size fuera de 1..100 lo da
# FastAPI automáticamente por los Query(ge/le); el 422 de page>pages lo calcula el service (IN-01).
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.mascotas import schemas, service

router = APIRouter()


@router.post("/mascotas/", response_model=schemas.MascotaRead, status_code=status.HTTP_201_CREATED)
async def crear_mascota(payload: schemas.MascotaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_mascota(session, payload)


@router.get("/mascotas/", response_model=schemas.MascotaPage)
async def listar_mascotas(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    return await service.listar_mascotas(session, page, size)


@router.get("/mascotas/{mascota_id}", response_model=schemas.MascotaRead)
async def obtener_mascota(mascota_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_mascota(session, mascota_id)
