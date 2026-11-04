# Router del módulo laboratorio (C-09, US-601 CA-2): GET /laboratorio/stock/{vacuna}.
# Handler async def; la llamada bloqueante se descarga en el service (RN-AS-01/RN-AS-02).
from fastapi import APIRouter

from app.modules.laboratorio import service

router = APIRouter()


@router.get("/laboratorio/stock/{vacuna}")
async def stock_vacuna(vacuna: str):
    """Responde {"vacuna": ..., "stock": ...} llamando a consultar_stock fuera del bucle de eventos."""
    return await service.obtener_stock(vacuna)
