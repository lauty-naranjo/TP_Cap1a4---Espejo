# Service del módulo laboratorio (C-09, US-601, RN-AS-01/RN-AS-02).
# Sin persistencia (IN-02): no hay models.py; la respuesta es un dict inline {"vacuna", "stock"}.
# La función bloqueante de la cátedra se ejecuta FUERA del bucle de eventos (offload a hilo, DD-07/QA-03).
from typing import Dict

from anyio import to_thread

from app.modules.laboratorio.cliente import consultar_stock


async def obtener_stock(vacuna: str) -> Dict[str, object]:
    """RN-AS-02: consulta el stock llamando a `consultar_stock` sin modificarla y fuera del event loop.

    `anyio.to_thread.run_sync` descarga la función sincrónica (time.sleep(1)) a un hilo del worker
    pool, de modo que el bucle sigue atendiendo otras peticiones (GET /health/live responde al
    instante, caso C-09).
    """
    stock: int = await to_thread.run_sync(consultar_stock, vacuna)
    return {"vacuna": vacuna, "stock": stock}
