# Tests del módulo laboratorio (C-09, US-601, RN-AS-01/RN-AS-02) — change c-09-laboratorio-offload.
# Sin persistencia (IN-02): no tocan la base. Verifican la respuesta y que la función bloqueante
# (time.sleep(1)) se ejecuta FUERA del bucle de eventos (offload a hilo → paraleliza, no serializa).
import asyncio
import time

from app.modules.laboratorio import service


def test_obtener_stock_devuelve_dict_con_stock():
    async def body():
        dto = await service.obtener_stock("vacuna")
        assert dto == {"vacuna": "vacuna", "stock": 16}  # 10 + len("vacuna")

    asyncio.run(body())


def test_obtener_stock_usa_la_funcion_sin_modificar():
    async def body():
        dto = await service.obtener_stock("antirrabica")
        assert dto["stock"] == 21  # 10 + len("antirrabica")

    asyncio.run(body())


def test_offload_paraleliza_tres_consultas():
    """RN-AS-02: 3 consultas de 1 s cada una, descargadas a hilos, corren en paralelo (~1 s), no en
    serie (~3 s). Si la llamada bloqueante corriera dentro del bucle, este test superaría el umbral."""

    async def body():
        inicio = time.perf_counter()
        resultados = await asyncio.gather(*[service.obtener_stock("vacuna") for _ in range(3)])
        duracion = time.perf_counter() - inicio

        assert resultados == [{"vacuna": "vacuna", "stock": 16}] * 3
        # 3 × 1 s en paralelo ≈ 1 s; en serie serían ≈ 3 s. El umbral distingue ambos casos.
        assert duracion < 2.5, f"offload no paralelizó: tardó {duracion:.2f}s (esperado < 2.5s)"

    asyncio.run(body())
