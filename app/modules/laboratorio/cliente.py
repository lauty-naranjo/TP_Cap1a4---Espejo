# cliente.py — módulo entregado por la cátedra (US-601 CA-1, SU-05).
# Biblioteca del laboratorio que provee las vacunas: sincrónica, sin variante asincrónica.
# Se usa SIN modificarla; el service la descarga fuera del bucle de eventos (RN-AS-02).
import time


def consultar_stock(vacuna: str) -> int:
    """Biblioteca del laboratorio: sincrónica, tarda un segundo."""
    time.sleep(1)
    return 10 + len(vacuna)
