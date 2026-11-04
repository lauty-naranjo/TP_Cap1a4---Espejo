# DTOs del módulo practicas (C-06, US-205): separados de los modelos (RN-HTTP-02).
# Dinero en Decimal, nunca float (RN-DS-01). precio > 0 se valida en el DTO (RN-04, 422) y
# además lo respalda el CHECK de la base.
from decimal import Decimal

from sqlmodel import Field, SQLModel


class PracticaCreate(SQLModel):
    nombre: str
    precio: Decimal = Field(gt=0)  # RN-04: precio > 0 → 422 si no cumple el contrato


class PracticaRead(SQLModel):
    id: int
    nombre: str
    precio: Decimal
