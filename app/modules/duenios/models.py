# Modelos del módulo duenios (C-03): Duenio y FichaDuenio (relación 1:1).
# Nombres de tabla/columna obligatorios (SU-02): duenio, ficha_duenio. Sin renombrar ni quitar.
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Duenio(SQLModel, table=True):
    __tablename__ = "duenio"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(unique=True)  # RN-01: UNIQUE en la base

    # 1:1 — un dueño tiene como máximo una ficha (objeto, no lista; RN-REL-02).
    ficha: Optional["FichaDuenio"] = Relationship(back_populates="duenio")
    # Agregación 1:N — mascotas a nombre del dueño (RN-08 bloquea el borrado vía RESTRICT).
    mascotas: List["Mascota"] = Relationship(back_populates="duenio")


class FichaDuenio(SQLModel, table=True):
    __tablename__ = "ficha_duenio"

    id: Optional[int] = Field(default=None, primary_key=True)
    duenio_id: int = Field(foreign_key="duenio.id", unique=True)  # UNIQUE = el 1:1 (RN-03)
    telefono: str
    direccion: str

    duenio: Optional[Duenio] = Relationship(back_populates="ficha")
