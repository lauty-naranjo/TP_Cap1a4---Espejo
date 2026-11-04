# Modelos del módulo turnos (C-03): Turno y TurnoPractica (composición + M:N con datos).
# Nombres de tabla/columna obligatorios (SU-02): turno, turno_practica. TurnoPractica vive en turnos.
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


class Turno(SQLModel, table=True):
    __tablename__ = "turno"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_turno_total_no_negativo"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    # Asociación: FK a mascota con índice manual (sección 4.10).
    mascota_id: int = Field(foreign_key="mascota.id", index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # timestamptz
    motivo: str
    total: Decimal = Field(max_digits=12, decimal_places=2)  # NUMERIC(12,2), CHECK >= 0

    mascota: Optional["Mascota"] = Relationship(back_populates="turnos")
    # Composición: el borrado de las prácticas lo decide la base (ON DELETE CASCADE), no el ORM
    # (RN-INT-02, DD-05) → passive_deletes para que el ORM no intente vaciar/borrar las filas.
    practicas: List["TurnoPractica"] = Relationship(
        back_populates="turno",
        sa_relationship_kwargs={"passive_deletes": True},
    )


class TurnoPractica(SQLModel, table=True):
    __tablename__ = "turno_practica"
    __table_args__ = (
        CheckConstraint("precio_unitario > 0", name="ck_turno_practica_precio_positivo"),
    )

    # PK compuesta (RN-07) + FK turno_id con CASCADE (RN-09). Sin índice propio en turno_id:
    # la PK compuesta (turno_id, practica_id) ya sirve para buscar por turno (explicado en el README).
    turno_id: int = Field(primary_key=True, foreign_key="turno.id", ondelete="CASCADE")
    practica_id: int = Field(primary_key=True, foreign_key="practica.id", index=True)
    # Dato propio del M:N: el precio congelado al reservar (RN-06, RN-DS-02).
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)  # NUMERIC(10,2), CHECK > 0

    turno: Optional[Turno] = Relationship(back_populates="practicas")
    practica: Optional["Practica"] = Relationship(back_populates="turno_practicas")
