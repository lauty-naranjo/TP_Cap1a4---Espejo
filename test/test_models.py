# Tests de los modelos de dominio (C-03, US-301). Inspeccionan el esquema declarado vía
# SQLAlchemy/SQLModel (sin tocar la base): nombres de tabla/columna, restricciones, FKs, índices y
# relaciones. Los nombres son obligatorios (SU-02); la integridad la garantiza la base (DD-04).
from decimal import Decimal

import sqlalchemy as sa
from sqlmodel import SQLModel

# Importar en orden de dependencia (pobla el registry de SQLModel con las 6 tablas).
from app.modules.duenios.models import Duenio, FichaDuenio  # noqa: F401
from app.modules.practicas.models import Practica  # noqa: F401
from app.modules.mascotas.models import Mascota  # noqa: F401
from app.modules.turnos.models import Turno, TurnoPractica  # noqa: F401

TABLAS = ["duenio", "ficha_duenio", "mascota", "practica", "turno", "turno_practica"]

COLUMNAS = {
    "duenio": {"id", "nombre", "email"},
    "ficha_duenio": {"id", "duenio_id", "telefono", "direccion"},
    "mascota": {"id", "nombre", "especie", "duenio_id"},
    "practica": {"id", "nombre", "precio"},
    "turno": {"id", "mascota_id", "fecha", "motivo", "total"},
    "turno_practica": {"turno_id", "practica_id", "precio_unitario"},
}


def _tabla(nombre):
    return SQLModel.metadata.tables[nombre]


def _unique_por_columna(tabla, *columnas):
    """Columnas que están cubiertas por una restricción UNIQUE (constraint o índice unique)."""
    unicas = set()
    for c in tabla.constraints:
        if isinstance(c, sa.UniqueConstraint):
            cols = {col.name for col in c.columns}
            if len(cols) == 1:
                unicas |= cols
    for ix in tabla.indexes:
        if ix.unique and len(ix.columns) == 1:
            unicas.add(ix.columns[0].name)
    return unicas


def _check(tabla, fragmento):
    return any(
        isinstance(c, sa.CheckConstraint) and fragmento in str(c.sqltext)
        for c in tabla.constraints
    )


def _fk_ondelete(tabla, columna):
    col = tabla.columns[columna]
    fks = list(col.foreign_keys)
    assert len(fks) == 1, f"{tabla.name}.{columna} debe tener exactamente una FK"
    return fks[0].ondelete


def _tiene_indice_propio(tabla, columna):
    col = tabla.columns[columna]
    return any(list(ix.columns) == [col] for ix in tabla.indexes)


def _relacion(clase, nombre):
    return sa.inspect(clase).relationships[nombre]


def test_seis_tablas_registradas():
    assert set(TABLAS) <= set(SQLModel.metadata.tables.keys())


def test_nombres_de_columnas_obligatorios():
    for nombre, esperadas in COLUMNAS.items():
        reales = set(_tabla(nombre).columns.keys())
        assert reales == esperadas, f"{nombre}: {reales} != {esperadas}"


def test_uniques():
    assert "email" in _unique_por_columna(_tabla("duenio"))
    assert "nombre" in _unique_por_columna(_tabla("practica"))
    assert "duenio_id" in _unique_por_columna(_tabla("ficha_duenio"))


def test_checks():
    assert _check(_tabla("practica"), "precio > 0")
    assert _check(_tabla("turno"), "total >= 0")
    assert _check(_tabla("turno_practica"), "precio_unitario > 0")


def test_fks_y_ondelete():
    assert _fk_ondelete(_tabla("mascota"), "duenio_id") == "RESTRICT"
    assert _fk_ondelete(_tabla("turno_practica"), "turno_id") == "CASCADE"
    # Lados sin regla de borrado dictada por la consigna.
    assert _fk_ondelete(_tabla("turno"), "mascota_id") is None
    assert _fk_ondelete(_tabla("turno_practica"), "practica_id") is None


def test_pk_compuesta_turno_practica():
    pk = _tabla("turno_practica").primary_key
    assert {c.name for c in pk.columns} == {"turno_id", "practica_id"}


def test_indices_en_fks():
    assert _tiene_indice_propio(_tabla("mascota"), "duenio_id")
    assert _tiene_indice_propio(_tabla("turno"), "mascota_id")
    assert _tiene_indice_propio(_tabla("turno_practica"), "practica_id")
    # turno_id no lleva índice propio: lo cubre la PK compuesta.
    assert not _tiene_indice_propio(_tabla("turno_practica"), "turno_id")


def test_relaciones_back_populates_y_ficha_objeto():
    ficha = _relacion(Duenio, "ficha")
    assert ficha.uselist is False, "Duenio.ficha debe ser objeto, no lista"
    assert ficha.back_populates == "duenio"
    assert _relacion(FichaDuenio, "duenio").back_populates == "ficha"

    assert _relacion(Duenio, "mascotas").uselist is True
    assert _relacion(Duenio, "mascotas").back_populates == "duenio"
    assert _relacion(Mascota, "duenio").back_populates == "mascotas"

    assert _relacion(Mascota, "turnos").back_populates == "mascota"
    assert _relacion(Turno, "mascota").back_populates == "turnos"

    assert _relacion(Turno, "practicas").back_populates == "turno"
    assert _relacion(TurnoPractica, "turno").back_populates == "practicas"

    assert _relacion(Practica, "turno_practicas").back_populates == "practica"
    assert _relacion(TurnoPractica, "practica").back_populates == "turno_practicas"


def test_passive_deletes_en_composicion():
    assert _relacion(Turno, "practicas").passive_deletes is True


def test_dinero_decimal_y_numeric():
    precio = _tabla("practica").columns["precio"].type
    total = _tabla("turno").columns["total"].type
    unitario = _tabla("turno_practica").columns["precio_unitario"].type

    for col, precision, escala in [(precio, 10, 2), (total, 12, 2), (unitario, 10, 2)]:
        assert isinstance(col, sa.Numeric), f"{col} debe ser NUMERIC"
        assert col.precision == precision
        assert col.scale == escala
        assert col.python_type is Decimal, f"{col} debe mapear a Decimal (nunca float)"
