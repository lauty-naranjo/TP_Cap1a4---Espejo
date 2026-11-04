# Router del módulo turnos (C-07, US-401): rutas HTTP — reciben, delegan y declaran la respuesta.
# Códigos de la consigna (RN-HTTP-01): 201 al crear, 204 al borrar, 404/409/422.
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.turnos import schemas, service

router = APIRouter()


@router.post("/turnos/", response_model=schemas.TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear_turno(payload: schemas.TurnoCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_turno(session, payload)


@router.delete("/turnos/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_turno(turno_id: int, session: AsyncSession = Depends(get_session)):
    await service.borrar_turno(session, turno_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/turnos/{turno_id}", response_model=schemas.TurnoRead)
async def obtener_turno(turno_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_turno(session, turno_id)
