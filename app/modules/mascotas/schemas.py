# DTOs del módulo mascotas (C-06, US-204): separados de los modelos de tabla (RN-HTTP-02).
# MascotaCreate trae duenio_id (en la agregación viaja un id). MascotaRead embebe el dueño en el
# detalle (joinedload) y lo deja null en el alta/listado para no disparar lazy load (RN-REL-03).
from typing import List, Optional

from sqlmodel import SQLModel


class DuenioResumen(SQLModel):
    """Dueño embebido en el detalle de una mascota (GET /mascotas/{id})."""

    id: int
    nombre: str
    email: str


class MascotaCreate(SQLModel):
    nombre: str
    especie: str
    duenio_id: int  # US-204 CA-1: en la agregación viaja un id de un dueño existente


class MascotaRead(SQLModel):
    id: int
    nombre: str
    especie: str
    duenio_id: int
    duenio: Optional[DuenioResumen] = None  # poblado solo en el detalle (joinedload a uno)


class MascotaPage(SQLModel):
    """Envoltorio de paginación de la sección 2.9 (RN-HTTP-04)."""

    items: List[MascotaRead]
    total: int
    page: int
    size: int
    pages: int
