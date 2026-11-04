# Tests de configuración por entorno (US-103) — change C-01.
# Se usa subprocess: el fail-fast vive en el arranque del proceso ("el proceso de la aplicación
# se inicia"), así aislamos el entorno y el .env real de cada escenario.
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_CONTENIDA_ENV = "postgresql+asyncpg://usuario:password@localhost:5432/veterinaria"


def _env_limpio(extra_env):
    """Entorno del subprocess sin DATABASE_URL (limpio) + extras."""
    env = {clave: valor for clave, valor in os.environ.items() if clave != "DATABASE_URL"}
    env["PYTHONPATH"] = REPO_ROOT
    env.update(extra_env)
    return env


def _importar_config(cwd, env):
    return subprocess.run(
        [sys.executable, "-c", "import app.core.config"],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def test_fail_fast_sin_env_ni_variable(tmp_path):
    """Escenario: .env ausente y variable indefinida → aborta con error claro."""
    assert not (tmp_path / ".env").exists()
    resultado = _importar_config(cwd=tmp_path, env=_env_limpio({}))
    assert resultado.returncode != 0
    assert "DATABASE_URL" in resultado.stderr
    assert "env.example" in resultado.stderr


def test_fail_fast_env_sin_variable(tmp_path):
    """Escenario: .env presente pero sin DATABASE_URL → mismo error claro de config faltante."""
    (tmp_path / ".env").write_text("OTRA_VARIABLE=algo\n", encoding="utf-8")
    resultado = _importar_config(cwd=tmp_path, env=_env_limpio({}))
    assert resultado.returncode != 0
    assert "DATABASE_URL" in resultado.stderr
    assert "env.example" in resultado.stderr


def test_lee_database_url_de_env(tmp_path):
    """Escenario: DATABASE_URL presente en .env → la carga y la expone intacta."""
    (tmp_path / ".env").write_text(
        "DATABASE_URL=postgresql+asyncpg://usuario:password@localhost:5432/veterinaria\n",
        encoding="utf-8",
    )
    env = _env_limpio({})
    codigo = "import app.core.config; print(app.core.config.DATABASE_URL)"
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == URL_CONTENIDA_ENV


def test_variable_del_entorno_sin_env(tmp_path):
    """Escenario: DATABASE_URL definida en el entorno (sin .env) → también se detecta."""
    env = _env_limpio({"DATABASE_URL": URL_CONTENIDA_ENV})
    codigo = "import app.core.config; print(app.core.config.DATABASE_URL)"
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stdout.strip() == URL_CONTENIDA_ENV
