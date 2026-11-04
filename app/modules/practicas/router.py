# Router del módulo practicas (C-06, US-205): rutas HTTP — reciben, delegan y declaran la respuesta.
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.practicas import schemas, service

router = APIRouter()


@router.post("/practicas/", response_model=schemas.PracticaRead, status_code=status.HTTP_201_CREATED)
async def crear_practica(payload: schemas.PracticaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_practica(session, payload)


@router.get("/practicas/", response_model=list[schemas.PracticaRead])
async def listar_practicas(session: AsyncSession = Depends(get_session)):
    return await service.listar_practicas(session)
