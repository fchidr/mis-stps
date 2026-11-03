# Mejora el script en velocidad, reutilización de conexiones y scraping asíncrono

Aquí tienes una versión avanzada y optimizada del scraper con:

* scraping completamente asíncrono (`aiohttp`)
* reutilización de conexiones HTTP
* límite de concurrencia
* parsing eficiente
* reintentos automáticos
* timeout configurable
* mejor rendimiento para miles de startups
* manejo robusto de errores
* URLs absolutas automáticas

Esta versión puede ser entre 20x y 100x más rápida que la secuencial.

Instalación:

```bash
pip install aiohttp beautifulsoup4 lxml
```

Script optimizado:

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from aiohttp import ClientTimeout

# =========================================================
# CONFIGURACIÓN
# =========================================================

BASE_URL = "https://ejemplo.com"

CONCURRENCIA = 20
TIMEOUT = 20
REINTENTOS = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# =========================================================
# DATOS
# =========================================================

resultados = [
    {
        "empresa": "MediaForm",
        "node_id": "113",
        "enlace": "/startups/mediaform",
        "logo": "/sites/default/files/2025-08/MediaForm.png",
        "etiqueta": "Gaming",
        "etiqueta_url": "/taxonomy/term/12"
    }
]

# =========================================================
# HELPERS
# =========================================================

def limpiar_texto(texto):

    if not texto:
        return ""

    return " ".join(texto.split())


def url_absoluta(url):

    if not url:
        return ""

    return urljoin(BASE_URL, url)

# =========================================================
# EXTRACCIÓN HTML
# =========================================================

def extraer_descripcion(soup):

    el = soup.select_one(
        ".startup-description "
        ".field--name-field-descripcion "
        ".field__item"
    )

    return limpiar_texto(
        el.get_text()
    ) if el else ""


def extraer_descripcion_larga(soup):

    el = soup.select_one(
        ".solution-section "
        ".field--name-field-solucion "
        ".field__item p"
    )

    return limpiar_texto(
        el.get_text()
    ) if el else ""


def extraer_video(soup):

    source = soup.select_one(
        ".video-container video source"
    )

    if source and source.get("src"):

        return url_absoluta(
            source.get("src")
        )

    return ""


def extraer_trabajadores(soup):

    trabajadores = []

    bloques = soup.select(
        ".trabajador-startup-content"
    )

    for bloque in bloques:

        nombre_el = bloque.select_one(
            ".trabajador-startup-nombre .field__item"
        )

        cargo_el = bloque.select_one(
            ".trabajador-startup-cargo .field__item"
        )

        img_el = bloque.select_one(
            ".trabajador-startup-imagen img"
        )

        imagen = ""

        if img_el:

            imagen_src = (
                img_el.get("src")
                or img_el.get("data-src")
            )

            imagen = url_absoluta(imagen_src)

        trabajadores.append({
            "nombre": limpiar_texto(
                nombre_el.get_text()
            ) if nombre_el else "",

            "cargo": limpiar_texto(
                cargo_el.get_text()
            ) if cargo_el else "",

            "imagen": imagen
        })

    return trabajadores

# =========================================================
# FETCH ASÍNCRONO
# =========================================================

async def descargar_html(session, url):

    for intento in range(REINTENTOS):

        try:

            async with session.get(url) as response:

                response.raise_for_status()

                return await response.text()

        except Exception as e:

            print(
                f"Reintento {intento+1} "
                f"fallido para {url}: {e}"
            )

            await asyncio.sleep(1)

    return None

# =========================================================
# PROCESAMIENTO STARTUP
# =========================================================

async def procesar_startup(
    session,
    semaphore,
    item
):

    async with semaphore:

        enlace = item.get("enlace")

        if not enlace:

            item["descripcion"] = ""
            item["descripcion_larga"] = ""
            item["video_presentacion"] = ""
            item["trabajadores"] = []

            return item

        url = url_absoluta(enlace)

        print(f"Procesando: {url}")

        html = await descargar_html(
            session,
            url
        )

        if not html:

            item["descripcion"] = ""
            item["descripcion_larga"] = ""
            item["video_presentacion"] = ""
            item["trabajadores"] = []

            return item

        # =====================================
        # PARSING
        # =====================================

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        # =====================================
        # EXTRACCIONES
        # =====================================

        item["descripcion"] = (
            extraer_descripcion(soup)
        )

        item["descripcion_larga"] = (
            extraer_descripcion_larga(soup)
        )

        item["video_presentacion"] = (
            extraer_video(soup)
        )

        item["trabajadores"] = (
            extraer_trabajadores(soup)
        )

        # =====================================
        # LOGO ABSOLUTO
        # =====================================

        if item.get("logo"):

            item["logo"] = url_absoluta(
                item["logo"]
            )

        return item

# =========================================================
# PROCESAMIENTO GLOBAL
# =========================================================

async def procesar_startups(lista_resultados):

    timeout = ClientTimeout(
        total=TIMEOUT
    )

    connector = aiohttp.TCPConnector(
        limit=CONCURRENCIA,
        ssl=False
    )

    semaphore = asyncio.Semaphore(
        CONCURRENCIA
    )

    async with aiohttp.ClientSession(
        headers=HEADERS,
        timeout=timeout,
        connector=connector
    ) as session:

        tareas = [

            procesar_startup(
                session,
                semaphore,
                item
            )

            for item in lista_resultados
        ]

        resultados = await asyncio.gather(
            *tareas
        )

        return resultados

# =========================================================
# MAIN
# =========================================================

async def main():

    resultados_finales = await procesar_startups(
        resultados
    )

    print(
        json.dumps(
            resultados_finales,
            indent=2,
            ensure_ascii=False
        )
    )

    # =====================================
    # GUARDAR JSON
    # =====================================

    with open(
        "startups.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            resultados_finales,
            f,
            ensure_ascii=False,
            indent=2
        )

if __name__ == "__main__":

    asyncio.run(main())
```

Mejoras clave incluidas:

| Mejora                 | Beneficio                           |
| ---------------------- | ----------------------------------- |
| `aiohttp`              | conexiones asíncronas ultra rápidas |
| `TCPConnector`         | reutilización real de sockets       |
| `Semaphore`            | evita saturar servidor              |
| `asyncio.gather`       | paralelismo masivo                  |
| `lxml`                 | parsing HTML mucho más rápido       |
| reintentos automáticos | mayor resiliencia                   |
| `ClientSession`        | pool de conexiones                  |
| timeout global         | evita bloqueos                      |
| URLs absolutas         | datos listos para usar              |

Configuraciones recomendadas:

Para scraping moderado:

```python
CONCURRENCIA = 20
```

Para servidores potentes:

```python
CONCURRENCIA = 100
```

Para scraping agresivo:

```python
CONCURRENCIA = 300
```

Siguientes optimizaciones posibles:

* `uvloop` → acelera asyncio
* `selectolax` → parser HTML 5-10x más rápido que BeautifulSoup
* compresión gzip/brotli
* rotación de proxies
* cache Redis
* exportación streaming NDJSON
* cola distribuida con RabbitMQ/Kafka
* Playwright async para JS rendering
* scraping distribuido multi-servidor
* detección automática anti-bot
* fingerprints TLS reales
* persistencia incremental async a PostgreSQL/MongoDB

Para datasets enormes (100k+ páginas), la combinación más rápida sería:

* `aiohttp`
* `selectolax`
* `uvloop`
* escritura NDJSON streaming
* concurrencia adaptativa dinámica

---
