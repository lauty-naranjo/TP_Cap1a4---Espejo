# Modelos del módulo mascotas (C-03): Mascota (agregación con el dueño).
# Nombre de tabla/columna obligatorio (SU-02): mascota. FK duenio_id ON DELETE RESTRICT + índice.
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Mascota(SQLModel, table=True):
    __tablename__ = "mascota"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    especie: str
    # Agregación: FK con RESTRICT (RN-08) e índice manual (PostgreSQL no lo crea solo, sección 4.10).
    duenio_id: int = Field(foreign_key="duenio.id", index=True, ondelete="RESTRICT")

    duenio: Optional["Duenio"] = Relationship(back_populates="mascotas")
    # Asociación Turno → Mascota, declarada en el otro extremo (RN-REL-01).
    turnos: List["Turno"] = Relationship(back_populates="mascota")
