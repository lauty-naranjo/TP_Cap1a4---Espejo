# Casos de prueba de la consigna (C-10 · US-701)

Estos archivos demuestran los 9 casos mínimos de la consigna (`C-01` … `C-09`). Se corren **en orden**
sobre el estado conocido que deja `python reiniciar.py`.

## Preparación

```bash
python reiniciar.py                      # deja el seed de C-04 (2 dueños, 3 mascotas, 4 prácticas, 1 turno)
uvicorn app.main:app --reload            # servidor en http://localhost:8000
```

Para la **evidencia del caso C-07** (consultas en la consola) arrancá el servidor con el log de SQL:

```bash
# PowerShell
$env:SQL_ECHO="true"; uvicorn app.main:app --reload
# bash
SQL_ECHO=true uvicorn app.main:app --reload
```

## Archivos

| Archivo | Caso | Qué demuestra | Resultado esperado |
|---|---|---|---|
| `C-01.http` | C-01 | Parámetro de ruta no entero (`/duenios/abc`) | **422**, sin ejecutar el handler |
| `C-02.http` | C-02 | Email de dueño / nombre de práctica repetido | **409** con mensaje propio |
| `C-03.http` | C-03 | Segunda ficha para el mismo dueño | **409** |
| `C-04.http` | C-04 | Mascota con dueño inexistente y turno con práctica inexistente | **409**, del turno no queda nada |
| `C-05.http` | C-05 | Borrar dueño con mascotas / borrar turno | **409** el dueño; **204** el turno |
| `C-06.http` | C-06 | Turno válido con dos prácticas | **201** con precios copiados y total |
| `C-07.http` | C-07 | Detalle de turno con 1 y con 3 prácticas | **misma cantidad de consultas** (echo) |
| `C-08.sql` | C-08 | `UPDATE practica SET precio = 0` directo en la base | la base lo rechaza por el **CHECK** |
| `C-09.http` | C-09 | Consultas al laboratorio + `GET /health/live` | el health responde de inmediato |

> Los `.http` son compatibles con VS Code *REST Client* e IntelliJ *HTTP Client* (`###` separa
> peticiones, `#` son comentarios). El caso `C-08` va en `.sql` aparte (se ejecuta con `psql`).
