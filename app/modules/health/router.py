# Router de health (C-02, US-102, RN-HL-01/RN-HL-02): /health/live y /health/ready.
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health/live")
async def health_live():
    """RN-HL-01: liveness del proceso; responde 200 sin consultar la base."""
    return {"estado": "vivo"}


@router.get("/health/ready")
async def health_ready(session: AsyncSession = Depends(get_session)):
    """RN-HL-02 / US-102 CA-1/CA-2: readiness con SELECT 1; 200 si la base contesta, 503 si no."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        # El detalle del error queda en el log, no en la respuesta (diseño D4).
        logger.exception("Health check /health/ready: la base no respondió el SELECT 1")
        return JSONResponse(status_code=503, content={"estado": "no_disponible"})
    return JSONResponse(status_code=200, content={"estado": "listo"})
