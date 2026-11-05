# Tests del formato de entrega (C-11, US-801, Épica 8) — change c-11-delivery-readme.
# Contrato sobre ARCHIVOS: no importa `app`, no abre conexiones ni necesita PostgreSQL.
# Verifica CA-1..CA-4 de US-801 y que el README documente el chequeo final (CA-5).
import os
import re
import shutil
import subprocess
import unicodedata

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_PLACEHOLDER = "postgresql+asyncpg://usuario:password@localhost:5432/veterinaria"

# Secciones fijas del README (design D1). Se comparan por palabra clave del encabezado H2.
SECCIONES_OBLIGATORIAS = [
    "descripcion",
    "requisitos",
    "puesta en marcha",
    "configuracion",
    "modelo de datos",
    "evidencia",
    "casos de prueba",
    "estructura",
    "chequeo final",
]

# Pasos de la puesta en marcha, en el orden exigido por US-801 CA-2.
PASOS_PUESTA_EN_MARCHA = [
    "python -m venv .venv",
    "pip install -r requirements.txt",
    "env.example .env",
    "python reiniciar.py",
    "uvicorn app.main:app",
]

TABLAS = ["duenio", "ficha_duenio", "mascota", "practica", "turno", "turno_practica"]
CASOS = [f"C-{numero:02d}" for numero in range(1, 10)]
CONTEOS_SEED = ["2 duenos", "3 mascotas", "4 practicas", "1 turno"]


# --- Helpers puros (testeables con texto sintético) ---------------------------------


def _normalizar(texto):
    """Minúsculas y sin acentos, para comparar encabezados y prosa sin depender de tildes."""
    sin_tildes = unicodedata.normalize("NFKD", texto.lower())
    return "".join(caracter for caracter in sin_tildes if not unicodedata.combining(caracter))


def _ruta(relativa):
    return os.path.join(REPO_ROOT, relativa)


def _leer(relativa):
    ruta = _ruta(relativa)
    assert os.path.isfile(ruta), f"Falta el artefacto obligatorio de la entrega: {relativa}"
    with open(ruta, encoding="utf-8") as archivo:
        return archivo.read()


def _encabezados(texto):
    """Lista de (nivel, título) de los encabezados Markdown del texto."""
    return [
        (len(coincidencia.group(1)), coincidencia.group(2).strip())
        for coincidencia in re.finditer(r"^(#{1,6})\s+(.+)$", texto, re.MULTILINE)
    ]


def _faltas_secciones(texto):
    titulos_h2 = [_normalizar(titulo) for nivel, titulo in _encabezados(texto) if nivel == 2]
    return [
        seccion
        for seccion in SECCIONES_OBLIGATORIAS
        if not any(seccion in titulo for titulo in titulos_h2)
    ]


def _cuerpo_seccion(texto, clave):
    """Cuerpo del primer H2 cuyo título contiene `clave` (normalizada); None si no existe."""
    encabezados_h2 = list(re.finditer(r"^#{2}\s+(.+)$", texto, re.MULTILINE))
    for indice, encabezado in enumerate(encabezados_h2):
        if clave in _normalizar(encabezado.group(1)):
            inicio = encabezado.end()
            fin = (
                encabezados_h2[indice + 1].start()
                if indice + 1 < len(encabezados_h2)
                else len(texto)
            )
            return texto[inicio:fin]
    return None


def _pasos_faltantes(cuerpo):
    return [paso for paso in PASOS_PUESTA_EN_MARCHA if paso not in cuerpo]


def _pasos_desordenados(cuerpo):
    posiciones = [(cuerpo.index(paso), paso) for paso in PASOS_PUESTA_EN_MARCHA]
    return [
        siguiente
        for (posicion, _), (posicion_siguiente, siguiente) in zip(posiciones, posiciones[1:])
        if posicion >= posicion_siguiente
    ]


def _faltas_indice(texto):
    """CA-3: explicación real del índice de turno_practica, no una mención genérica."""
    normalizado = _normalizar(texto)
    faltas = []

    if "turno_practica_pkey" not in texto and "(turno_id, practica_id)" not in texto:
        faltas.append("no nombra la PK compuesta (turno_id, practica_id)")
    if "primera columna" not in normalizado:
        faltas.append("no explica que la PK indexa por su primera columna")
    if not re.search(r"(no (hace falta|lleva|necesita|requiere)|sin)\s+(un\s+)?indice", normalizado):
        faltas.append("no aclara que turno_id no lleva índice propio")
    if "practica_id" not in texto:
        faltas.append("no menciona practica_id")
    if "ix_turno_practica_practica_id" not in texto and not re.search(
        r"practica_id[^.]{0,120}(indice|indexa)", normalizado
    ):
        faltas.append("no explica el índice propio de practica_id")
    return faltas


def _faltas_evidencia(texto):
    """CA-4: fragmento de las 2 consultas fijas con 1 y con 3 prácticas + enlace al crudo."""
    normalizado = _normalizar(texto)
    faltas = []

    for caso in ("1 practica", "3 practicas"):
        if caso not in normalizado:
            faltas.append(f"no muestra el caso con {caso}")
    if "left outer join" not in normalizado and "left join" not in normalizado:
        faltas.append("no incluye el SQL de las consultas del detalle")
    if "2 consultas" not in normalizado:
        faltas.append("no afirma que son 2 consultas fijas")
    if "no crece" not in normalizado:
        faltas.append("no concluye que el número de consultas no crece")
    if "test/evidencia_c07.txt" not in texto:
        faltas.append("no enlaza test/evidencia_c07.txt")
    return faltas


def _urls_database(texto):
    return re.findall(r"postgresql\+asyncpg://[^\s`'\"<>)]+", texto)


def _credenciales_reales(texto):
    """Devuelve las URLs de conexión del texto que no usan el placeholder de la cátedra."""
    return [url for url in _urls_database(texto) if url != URL_PLACEHOLDER]


def _faltas_chequeo_final(texto):
    """CA-5: 6 tablas, conteos del seed y endpoints de health documentados."""
    normalizado = _normalizar(texto)
    faltas = [f"tabla {tabla}" for tabla in TABLAS if tabla not in normalizado]
    faltas += [f"seed {conteo}" for conteo in CONTEOS_SEED if conteo not in normalizado]
    faltas += [
        f"endpoint {endpoint}"
        for endpoint in ("/health/live", "/health/ready")
        if endpoint not in normalizado
    ]
    return faltas


def _casos_en_tabla(texto):
    """Casos C-0X en el orden en que aparecen en las filas de la tabla Markdown."""
    casos = []
    for linea in texto.splitlines():
        if linea.startswith("|") and "C-0" in linea:
            coincidencia = re.search(r"\bC-0\d\b", linea)
            if coincidencia:
                casos.append(coincidencia.group(0))
    return casos


def _entradas_env_example(texto):
    entradas = {}
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        clave, _, valor = linea.partition("=")
        entradas[clave.strip()] = valor.strip()
    return entradas


# --- CA-1: repositorio de entrega completo y sin secretos --------------------------


def test_artefactos_obligatorios_presentes():
    """US-801 CA-1: app/, requirements.txt, env.example, reiniciar.py, test/ y README.md."""
    for directorio in ("app", "test"):
        assert os.path.isdir(_ruta(directorio)), f"Falta el directorio obligatorio: {directorio}/"

    for archivo in ("README.md", "requirements.txt", "env.example", "reiniciar.py"):
        assert os.path.isfile(_ruta(archivo)), f"Falta el archivo obligatorio: {archivo}"

    for caso in CASOS:
        extension = "sql" if caso == "C-08" else "http"
        assert os.path.isfile(_ruta(f"test/{caso}.{extension}")), (
            f"Falta el caso de la consigna: test/{caso}.{extension}"
        )


def test_env_fuera_del_versionado():
    """US-801 CA-1 / RN: `.env` ignorado por .gitignore y nunca trackeado."""
    git = shutil.which("git")
    if git is None:
        pytest.skip("git no disponible: no se puede verificar el versionado")

    def ejecutar(*argumentos):
        return subprocess.run(
            [git, *argumentos],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

    ignorado = ejecutar("check-ignore", "-v", ".env")
    assert ignorado.returncode == 0, "`.env` debe estar excluido por el .gitignore"
    assert ".gitignore" in ignorado.stdout, f"la exclusión debe venir del .gitignore: {ignorado.stdout}"

    assert ejecutar("check-ignore", "env.example").returncode != 0, (
        "`env.example` no debe estar ignorado"
    )
    assert ejecutar("ls-files", "--error-unmatch", ".env").returncode != 0, (
        "`.env` está trackeado en git: se filtraron credenciales"
    )


def test_env_example_solo_placeholders():
    """US-801 CA-1: env.example declara sólo DATABASE_URL con usuario/password de placeholder."""
    entradas = _entradas_env_example(_leer("env.example"))

    assert list(entradas) == ["DATABASE_URL"], f"env.example sólo declara DATABASE_URL: {entradas}"
    assert entradas["DATABASE_URL"] == URL_PLACEHOLDER


def test_readme_sin_credenciales_reales():
    """US-801 CA-2: los ejemplos del README usan placeholders, no credenciales de trabajo."""
    readme = _leer("README.md")

    assert _urls_database(readme), "el README debe mostrar la forma de DATABASE_URL"
    assert _credenciales_reales(readme) == [], (
        "hay URLs de conexión que no usan el placeholder usuario:password"
    )
    for prohibido in ("postgres:postgres", "admin:admin", "root:root"):
        assert prohibido not in _normalizar(readme), f"credencial genérica prohibida: {prohibido}"


# --- CA-2: README con puesta en marcha desde cero ----------------------------------


def test_readme_tiene_las_secciones_obligatorias():
    """US-801 CA-2: el README cubre descripción, requisitos, puesta en marcha, datos, etc."""
    faltas = _faltas_secciones(_leer("README.md"))
    assert faltas == [], f"faltan secciones H2 en el README: {faltas}"


def test_readme_pasos_en_orden():
    """US-801 CA-2: venv → dependencias → .env → reiniciar.py → uvicorn, en ese orden."""
    cuerpo = _cuerpo_seccion(_leer("README.md"), "puesta en marcha")
    assert cuerpo is not None, "falta la sección 'Puesta en marcha'"

    faltantes = _pasos_faltantes(cuerpo)
    assert faltantes == [], f"faltan pasos en la puesta en marcha: {faltantes}"
    assert _pasos_desordenados(cuerpo) == [], (
        f"pasos fuera de orden en la puesta en marcha: {_pasos_desordenados(cuerpo)}"
    )


def test_readme_menciona_versiones_requeridas():
    """US-801 CA-2: requisitos Python 3.12 y PostgreSQL 16."""
    readme = _leer("README.md")
    normalizado = _normalizar(readme)

    assert "python 3.12" in normalizado, "el README debe indicar Python 3.12"
    assert "postgresql 16" in normalizado, "el README debe indicar PostgreSQL 16"


def test_readme_comandos_para_powershell_y_bash():
    """US-801 CA-2: activación del venv y SQL_ECHO en ambos shells."""
    readme = _leer("README.md")

    assert "Activate.ps1" in readme, "falta la activación del venv para PowerShell"
    assert "source .venv/bin/activate" in readme, "falta la activación del venv para bash"
    assert "$env:SQL_ECHO" in readme, "falta SQL_ECHO para PowerShell"
    assert "SQL_ECHO=true" in readme, "falta SQL_ECHO para bash"


# --- CA-3: explicación del índice de turno_practica.turno_id ----------------------


def test_readme_explica_el_indice_de_turno_practica():
    """US-801 CA-3 / US-301 CA-2: PK compuesta como índice por su primera columna."""
    faltas = _faltas_indice(_cuerpo_seccion(_leer("README.md"), "modelo de datos") or "")
    assert faltas == [], f"la explicación del índice está incompleta: {faltas}"


def test_readme_documenta_las_6_tablas():
    """US-801 CA-3: el modelo de datos enumera las 6 tablas del esquema."""
    cuerpo = _normalizar(_cuerpo_seccion(_leer("README.md"), "modelo de datos") or "")
    faltantes = [tabla for tabla in TABLAS if tabla not in cuerpo]
    assert faltantes == [], f"el modelo de datos no menciona: {faltantes}"


# --- CA-4: evidencia del caso C-07 integrada --------------------------------------


def test_readme_integra_la_evidencia_c07():
    """US-801 CA-4: fragmento con 1 vs 3 prácticas, 2 consultas fijas y enlace al crudo."""
    faltas = _faltas_evidencia(_cuerpo_seccion(_leer("README.md"), "evidencia") or "")
    assert faltas == [], f"la evidencia C-07 del README está incompleta: {faltas}"


def test_evidencia_c07_cruda_conserva_los_dos_casos():
    """US-801 CA-4: test/evidencia_c07.txt contiene 1 y 3 prácticas y la conclusión."""
    evidencia = _leer("test/evidencia_c07.txt")
    normalizado = _normalizar(evidencia)

    assert "1 practica" in normalizado, "la evidencia cruda no tiene el caso de 1 práctica"
    assert "3 practicas" in normalizado, "la evidencia cruda no tiene el caso de 3 prácticas"
    assert "select turno" in normalizado, "falta la consulta del turno (joinedload)"
    assert "select turno_practica" in normalizado, "falta la consulta de las prácticas (selectinload)"
    assert "mismas 2 consultas" in normalizado, "falta la conclusión de 2 consultas fijas"
    assert "no crece" in normalizado, "falta la conclusión de que el número no crece"


# --- CA-5: chequeo final documentado ----------------------------------------------


def test_readme_documenta_el_chequeo_final():
    """US-801 CA-5: base vacía → reiniciar.py → 6 tablas + seed → health/ready."""
    cuerpo = _cuerpo_seccion(_leer("README.md"), "chequeo final") or ""
    faltas = _faltas_chequeo_final(cuerpo)
    assert faltas == [], f"el chequeo final está incompleto: {faltas}"


def test_readme_normaliza_la_fecha_a_utc():
    """QA-06: el ejemplo del README usa la respuesta real normalizada a UTC con Z."""
    readme = _leer("README.md")

    assert "2026-11-12T10:30:00-03:00" in readme, "falta la entrada con offset -03:00"
    assert "2026-11-12T13:30:00Z" in readme, "falta la respuesta normalizada a UTC con Z"


def test_readme_documenta_los_9_casos_en_orden():
    """US-701 / CA-4: tabla de C-01..C-09 en orden de ejecución."""
    cuerpo = _cuerpo_seccion(_leer("README.md"), "casos de prueba")
    assert cuerpo is not None, "falta la sección 'Casos de prueba'"

    assert _casos_en_tabla(cuerpo) == CASOS, (
        f"la tabla debe listar C-01..C-09 en orden de ejecución: {_casos_en_tabla(cuerpo)}"
    )


def test_readme_declara_alcance_sin_ui_ni_auth():
    """US-801: nota de alcance — API REST sin UI ni autenticación."""
    normalizado = _normalizar(_leer("README.md"))

    assert "api rest" in normalizado, "el README debe declarar que es una API REST"
    assert "sin ui" in normalizado or "sin interfaz" in normalizado, "falta la nota 'sin UI'"
    assert "sin auth" in normalizado or "sin autenticacion" in normalizado, (
        "falta la nota 'sin autenticación'"
    )


# --- 1.3: el contrato no depende de PostgreSQL ni de la app ------------------------


def test_contrato_de_entrega_no_importa_la_aplicacion():
    """El test de entrega es de archivos: no importa app.main ni app.core.database."""
    with open(os.path.abspath(__file__), encoding="utf-8") as archivo:
        codigo = archivo.read()

    imports_de_app = re.findall(r"^\s*(?:from|import)\s+app[.\s]", codigo, re.MULTILINE)
    assert imports_de_app == [], f"el test de entrega no debe importar la app: {imports_de_app}"


# --- Triangulación: los helpers rechazan entregas incompletas ----------------------
# Estos casos usan texto sintético distinto del README real: demuestran que las
# verificaciones no son tautológicas (un README mal armado efectivamente falla).


def test_helper_secciones_detecta_una_seccion_faltante():
    texto_incompleto = "# Proyecto\n\n## Descripción\n\n## Stack\n\n## Requisitos\n"
    assert "modelo de datos" in _faltas_secciones(texto_incompleto)


def test_helper_orden_detecta_pasos_invertidos():
    texto_invertido = "\n".join(reversed(PASOS_PUESTA_EN_MARCHA))
    assert _pasos_faltantes(texto_invertido) == []
    assert _pasos_desordenados(texto_invertido) != []


def test_helper_indice_detecta_una_explicacion_generica():
    generico = "La tabla turno_practica guarda las prácticas reservadas de cada turno."
    assert _faltas_indice(generico) != []

    explicito = (
        "La PK compuesta turno_practica_pkey (turno_id, practica_id) indexa por su primera columna, "
        "así que turno_id no lleva un índice propio; practica_id tiene "
        "ix_turno_practica_practica_id porque no es la primera columna."
    )
    assert _faltas_indice(explicito) == []


def test_helper_evidencia_detecta_la_falta_de_conclusion():
    sin_conclusion = (
        "DETALLE CON 1 PRÁCTICA\nDETALLE CON 3 PRÁCTICAS\n"
        "FROM turno LEFT OUTER JOIN mascota\n"
        "FROM turno_practica LEFT OUTER JOIN practica\n"
        "test/evidencia_c07.txt\n"
    )
    faltas = _faltas_evidencia(sin_conclusion)
    assert any("2 consultas" in falta for falta in faltas)
    assert any("no crece" in falta for falta in faltas)


def test_helper_credenciales_detecta_una_url_real():
    real = "postgresql+asyncpg://postgres:secreto@localhost:5432/veterinaria"
    assert _credenciales_reales(real) == [real]
    assert _credenciales_reales(f"`{URL_PLACEHOLDER}`") == []


def test_helper_chequeo_final_detecta_el_seed_faltante():
    solo_tablas = (
        "duenio, ficha_duenio, mascota, practica, turno, turno_practica; "
        "/health/live y /health/ready"
    )
    faltas = _faltas_chequeo_final(solo_tablas)
    assert any("seed 2 duenos" in falta for falta in faltas)
    assert any("seed 4 practicas" in falta for falta in faltas)


def test_helper_casos_detecta_el_orden_incorrecto():
    tabla_invertida = "| 1 | `C-02.http` | C-02 |\n| 2 | `C-01.http` | C-01 |\n"
    assert _casos_en_tabla(tabla_invertida) == ["C-02", "C-01"]
