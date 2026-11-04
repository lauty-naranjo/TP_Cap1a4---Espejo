# Modelos del módulo practicas (C-03): Practica (catálogo de servicios con precio).
# Nombre de tabla/columna obligatorio (SU-02): practica. Dinero en Decimal, nunca float (RN-DS-01).
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel


class Practica(SQLModel, table=True):
    __tablename__ = "practica"
    __table_args__ = (CheckConstraint("precio > 0", name="ck_practica_precio_positivo"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True)  # RN-02: UNIQUE en la base
    precio: Decimal = Field(max_digits=10, decimal_places=2)  # NUMERIC(10,2), CHECK > 0

    # M:N con datos vía turno_practica (RN-06: el precio cobrado es de la relación).
    turno_practicas: List["TurnoPractica"] = Relationship(back_populates="practica")
