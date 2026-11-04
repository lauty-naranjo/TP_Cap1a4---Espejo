# Router del módulo duenios (C-05): rutas HTTP — reciben, delegan y declaran la respuesta.
# Códigos de la consigna (RN-HTTP-01): 201/200/204, 404, 409, 422 (el 422 de id no entero lo da
# FastAPI automáticamente por el path param tipado `int`, caso C-01).
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.modules.duenios import schemas, service

router = APIRouter()


@router.post("/duenios/", response_model=schemas.DuenioRead, status_code=status.HTTP_201_CREATED)
async def crear_duenio(
    payload: schemas.DuenioCreate, session: AsyncSession = Depends(get_session)
):
    return await service.crear_duenio(session, payload)


@router.get("/duenios/{duenio_id}", response_model=schemas.DuenioRead)
async def obtener_duenio(duenio_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_duenio(session, duenio_id)


@router.patch("/duenios/{duenio_id}", response_model=schemas.DuenioRead)
async def actualizar_duenio(
    duenio_id: int, payload: schemas.DuenioUpdate, session: AsyncSession = Depends(get_session)
):
    return await service.actualizar_duenio(session, duenio_id, payload)


@router.delete("/duenios/{duenio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_duenio(duenio_id: int, session: AsyncSession = Depends(get_session)):
    await service.borrar_duenio(session, duenio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/duenios/{duenio_id}/ficha",
    response_model=schemas.FichaRead,
    status_code=status.HTTP_201_CREATED,
)
async def crear_ficha(
    duenio_id: int, payload: schemas.FichaCreate, session: AsyncSession = Depends(get_session)
):
    return await service.crear_ficha(session, duenio_id, payload)


@router.get("/duenios/{duenio_id}/mascotas", response_model=list[schemas.MascotaRead])
async def obtener_mascotas(duenio_id: int, session: AsyncSession = Depends(get_session)):
    return await service.obtener_mascotas_duenio(session, duenio_id)
