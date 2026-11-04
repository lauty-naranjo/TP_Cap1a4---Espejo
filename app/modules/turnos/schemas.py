# DTOs del módulo turnos (C-07, US-401): separados de los modelos (RN-HTTP-02).
# TurnoCreate trae mascota_id (asociación viaja id) y practicas:[{practica_id}] (composición viajan
# los datos que nacen con el turno). Ni precio ni total viajan en el DTO (RN-06).
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlmodel import Field, SQLModel


class PracticaTurnoCreate(SQLModel):
    practica_id: int  # composición: solo el id que identifica la práctica a reservar


class TurnoCreate(SQLModel):
    mascota_id: int
    fecha: datetime  # con zona horaria (timestamptz en la base)
    motivo: str
    practicas: List[PracticaTurnoCreate] = Field(min_length=1)  # RN-05: al menos una práctica


class MascotaResumen(SQLModel):
    """Mascota embebida en la respuesta del turno."""

    id: int
    nombre: str
    especie: str


class PracticaTurnoRead(SQLModel):
    """Práctica reservada con su precio congelado (precio_unitario, RN-DS-02)."""

    practica_id: int
    nombre: str
    precio_unitario: Decimal


class TurnoRead(SQLModel):
    id: int
    fecha: datetime
    motivo: str
    total: Decimal
    mascota: MascotaResumen
    practicas: List[PracticaTurnoRead]
