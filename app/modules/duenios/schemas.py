# DTOs del módulo duenios (C-05): separados de los modelos de tabla (RN-HTTP-02).
# Los de alta no llevan id; DuenioRead embebe la ficha (SU-04: null si aún no tiene).
from typing import List, Optional

from sqlmodel import SQLModel


class FichaRead(SQLModel):
    id: int
    telefono: str
    direccion: str


class DuenioRead(SQLModel):
    id: int
    nombre: str
    email: str
    ficha: Optional[FichaRead] = None


class DuenioCreate(SQLModel):
    nombre: str
    email: str


class DuenioUpdate(SQLModel):
    # Todos opcionales: el PATCH aplica sólo los campos enviados (exclude_unset, RN-HTTP-03).
    nombre: Optional[str] = None
    email: Optional[str] = None


class FichaCreate(SQLModel):
    telefono: str
    direccion: str


class MascotaRead(SQLModel):
    # Resumen para GET /duenios/{id}/mascotas (la colección se precarga con selectinload).
    id: int
    nombre: str
    especie: str
