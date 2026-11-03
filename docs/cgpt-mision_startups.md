# Aquí tienes un script profesional en Python usando `requests` + `lxml` para extraer todas las entidades `<article>` dentro del bloque:

```xpath
//div[@id='views-bootstrap-vista-startups-block-1']
```

El script extrae:

* Categoría / etiqueta

  * nombre
  * URL
* Logo

  * URL absoluta
* Startup

  * nombre
  * URL absoluta

---

```python
import requests
from lxml import html
from urllib.parse import urljoin
import json


BASE_URL = "https://example.com"   # <-- cambiar por dominio real
PAGE_URL = "https://example.com/startups"  # <-- cambiar URL real


def scrape_startups(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    tree = html.fromstring(response.content)

    articles = tree.xpath(
        "//div[@id='views-bootstrap-vista-startups-block-1']//article"
    )

    results = []

    for article in articles:

        # =========================
        # TAG / CATEGORÍA
        # =========================
        tag_name = article.xpath(
            ".//span[contains(@class, 'field__item tag-')]/a/text()"
        )

        tag_url = article.xpath(
            ".//span[contains(@class, 'field__item tag-')]/a/@href"
        )

        # =========================
        # LOGO
        # =========================
        logo_url = article.xpath(
            ".//div[@class='startup-teaser-logo']//img/@src"
        )

        # =========================
        # STARTUP
        # =========================
        startup_name = article.xpath(
            ".//div[@class='startup-teaser-name']//a//span/text()"
        )

        startup_url = article.xpath(
            ".//div[@class='startup-teaser-name']//a/@href"
        )

        item = {
            "tag_name": tag_name[0].strip() if tag_name else None,
            "tag_url": urljoin(BASE_URL, tag_url[0]) if tag_url else None,

            "logo_url": urljoin(BASE_URL, logo_url[0]) if logo_url else None,

            "startup_name": startup_name[0].strip() if startup_name else None,
            "startup_url": urljoin(BASE_URL, startup_url[0]) if startup_url else None,
        }

        results.append(item)

    return results


if __name__ == "__main__":

    startups = scrape_startups(PAGE_URL)

    print(json.dumps(startups, indent=4, ensure_ascii=False))
```

---

## Resultado esperado

```json
[
    {
        "tag_name": "Gaming",
        "tag_url": "https://example.com/taxonomy/term/12",
        "logo_url": "https://example.com/sites/default/files/2025-08/MediaForm.png",
        "startup_name": "MediaForm",
        "startup_url": "https://example.com/startups/mediaform"
    },
    {
        "tag_name": "Agrotech",
        "tag_url": "https://example.com/taxonomy/term/11",
        "logo_url": "https://example.com/sites/default/files/2025-08/Logo_Biogreen.jpg",
        "startup_name": "Biogreen Road",
        "startup_url": "https://example.com/startups/biogreen_road"
    }
]
```

---

## Ventajas de esta implementación

* Usa XPath relativo (`.`) dentro de cada `<article>`
* Convierte URLs relativas a absolutas con `urljoin`
* Maneja elementos faltantes sin romper
* Compatible con scraping masivo
* Fácil exportación a:

  * CSV
  * JSON
  * Base de datos
  * Pandas DataFrame

---

## Variante usando BeautifulSoup

Si prefieres `BeautifulSoup`, también puedes usar:

```bash
pip install beautifulsoup4 lxml
```

y te preparo una versión equivalente.

---

## Dependencias

Instalar:

```bash
pip install requests lxml
```

---

## Mejora recomendada para producción

Añadir:

* reintentos (`retry`)
* rotación de user agents
* soporte proxy
* paginación
* scraping asíncrono (`aiohttp`)
* exportación automática a CSV

Por ejemplo:

```python
import pandas as pd

df = pd.DataFrame(startups)
df.to_csv("startups.csv", index=False)
```

---

# Aquí tienes una versión más robusta y preparada para producción usando:

* `BeautifulSoup`
* exportación:

  * JSON
  * YAML
  * CSV
* rotación de User-Agents
* soporte opcional de proxies
* manejo de errores
* timeout
* sesión persistente
* URLs absolutas automáticas

---

# Dependencias

```bash
pip install requests beautifulsoup4 lxml pyyaml pandas fake-useragent
```

---

# Script completo

```python
import csv
import json
import random
import time
from urllib.parse import urljoin

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# =========================================================
# CONFIG
# =========================================================

BASE_URL = "https://example.com"
PAGE_URL = "https://example.com/startups"

OUTPUT_JSON = "startups.json"
OUTPUT_YAML = "startups.yaml"
OUTPUT_CSV = "startups.csv"

REQUEST_TIMEOUT = 30

# =========================================================
# USER AGENTS
# =========================================================

ua = UserAgent()

USER_AGENTS = [
    ua.chrome,
    ua.firefox,
    ua.safari,
    ua.edge,
]

# =========================================================
# PROXIES (OPCIONAL)
# =========================================================
# Ejemplo:
#
# PROXIES = {
#     "http": "http://user:password@proxyhost:port",
#     "https": "http://user:password@proxyhost:port",
# }
#
# O dejar None
# =========================================================

PROXIES = None


# =========================================================
# SESSION
# =========================================================

session = requests.Session()


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml",
        "Connection": "keep-alive",
    }


# =========================================================
# REQUEST
# =========================================================

def fetch_page(url, retries=3, delay=2):

    for attempt in range(1, retries + 1):

        try:
            response = session.get(
                url,
                headers=get_headers(),
                proxies=PROXIES,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as e:

            print(f"[ERROR] intento {attempt}: {e}")

            if attempt < retries:
                time.sleep(delay)

    return None


# =========================================================
# SCRAPER
# =========================================================

def scrape_startups(html):

    soup = BeautifulSoup(html, "lxml")

    container = soup.find(
        "div",
        id="views-bootstrap-vista-startups-block-1"
    )

    if not container:
        print("[ERROR] No se encontró el contenedor principal")
        return []

    articles = container.find_all("article")

    results = []

    for article in articles:

        # =================================================
        # TAG
        # =================================================

        tag_link = article.select_one(
            "span[class*='field__item tag-'] a"
        )

        tag_name = tag_link.get_text(strip=True) if tag_link else None

        tag_url = (
            urljoin(BASE_URL, tag_link["href"])
            if tag_link and tag_link.get("href")
            else None
        )

        # =================================================
        # LOGO
        # =================================================

        logo_img = article.select_one(
            "div.startup-teaser-logo img"
        )

        logo_url = (
            urljoin(BASE_URL, logo_img["src"])
            if logo_img and logo_img.get("src")
            else None
        )

        logo_alt = (
            logo_img.get("alt")
            if logo_img
            else None
        )

        # =================================================
        # STARTUP
        # =================================================

        startup_link = article.select_one(
            "div.startup-teaser-name a"
        )

        startup_name = (
            startup_link.get_text(strip=True)
            if startup_link
            else None
        )

        startup_url = (
            urljoin(BASE_URL, startup_link["href"])
            if startup_link and startup_link.get("href")
            else None
        )

        # =================================================
        # NODE ID
        # =================================================

        node_id = article.get("data-history-node-id")

        # =================================================
        # ITEM
        # =================================================

        item = {
            "node_id": node_id,

            "tag": {
                "name": tag_name,
                "url": tag_url,
            },

            "logo": {
                "url": logo_url,
                "alt": logo_alt,
            },

            "startup": {
                "name": startup_name,
                "url": startup_url,
            },
        }

        results.append(item)

    return results


# =========================================================
# EXPORT JSON
# =========================================================

def save_json(data, filename):

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"[OK] JSON guardado: {filename}")


# =========================================================
# EXPORT YAML
# =========================================================

def save_yaml(data, filename):

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False
        )

    print(f"[OK] YAML guardado: {filename}")


# =========================================================
# EXPORT CSV
# =========================================================

def save_csv(data, filename):

    rows = []

    for item in data:

        rows.append({
            "node_id": item["node_id"],

            "tag_name": item["tag"]["name"],
            "tag_url": item["tag"]["url"],

            "logo_url": item["logo"]["url"],
            "logo_alt": item["logo"]["alt"],

            "startup_name": item["startup"]["name"],
            "startup_url": item["startup"]["url"],
        })

    df = pd.DataFrame(rows)

    df.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"[OK] CSV guardado: {filename}")


# =========================================================
# MAIN
# =========================================================

def main():

    html = fetch_page(PAGE_URL)

    if not html:
        print("[ERROR] No se pudo descargar la página")
        return

    data = scrape_startups(html)

    print(f"[INFO] Startups extraídas: {len(data)}")

    save_json(data, OUTPUT_JSON)
    save_yaml(data, OUTPUT_YAML)
    save_csv(data, OUTPUT_CSV)


if __name__ == "__main__":
    main()
```

---

# Ejemplo de salida YAML

```yaml
- node_id: '113'
  tag:
    name: Gaming
    url: https://example.com/taxonomy/term/12
  logo:
    url: https://example.com/sites/default/files/2025-08/MediaForm.png
    alt: MediaForm
  startup:
    name: MediaForm
    url: https://example.com/startups/mediaform
```

---

# Uso con Proxy

Solo necesitas activar:

```python
PROXIES = {
    "http": "http://usuario:password@host:puerto",
    "https": "http://usuario:password@host:puerto",
}
```

---

# Mejoras recomendadas para scraping profesional

Puedes ampliar fácilmente con:

* rotación real de proxies
* `httpx` async
* `aiohttp`
* Selenium / Playwright
* detección antibot
* retries exponenciales
* cache local
* fingerprints TLS
* exportación a:

  * MongoDB
  * PostgreSQL
  * Elasticsearch
* scraping distribuido
* cola RabbitMQ/Kafka
* Docker

---

# Variante ultra rápida (async)

Si quieres, también puedo prepararte:

* versión async con `aiohttp`
* versión Selenium
* versión Playwright stealth
* scraper distribuido
* crawler multi-página
* extracción automática de paginación
* detección automática de taxonomías
* CLI profesional (`argparse`)
* logs avanzados (`loguru`)
* Dockerfile + requirements.txt
* estructura profesional tipo proyecto (`src/`, `services/`, `exporters/`)





---

# Como experto programador en Python, desarrolla un script que procese una lista de resultados de una serie de startups, y usando la clave "enlace" a la que se le sumará la URL base del sitio, procesa la página web dónde debe de extraerse y añadirse a la lista de resultados, los elementos "descripción" representado por el contenido de <div class="field__item">
<div class="startup-description">
  <div class="field field--name-field-descripcion field--type-string-long field--label-visually_hidden">
    <div class="field__label visually-hidden">Descripcion</div>
              <div class="field__item">Estudio especializado en paisajes sonoros y diseño de audio artesanal para videojuegos, cine y contenidos digitales</div>
          </div>
</div>

Las entradas de la lista de resultados tiene la forma:
  {
    "empresa": "MediaForm",
    "node_id": "113",
    "enlace": "/startups/mediaform",
    "logo": "/sites/default/files/2025-08/MediaForm.png",
    "etiqueta": "Gaming",
    "etiqueta_url": "/taxonomy/term/12"
  },


Aquí tienes un script profesional en Python que:

1. Recorre una lista de startups.
2. Construye la URL completa usando una URL base + `enlace`.
3. Descarga el HTML de cada página.
4. Extrae la descripción desde:

```html
<div class="field__item">...</div>
```

dentro del bloque:

```html
<div class="startup-description">
```

5. Añade el campo `descripcion` al resultado original.
6. Devuelve la lista enriquecida.

El script usa:

* `requests` para HTTP
* `BeautifulSoup` para parsing HTML
* manejo de errores
* timeout
* User-Agent realista
* extracción robusta

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import json

# URL base del sitio
BASE_URL = "https://ejemplo.com"

# Lista de resultados original
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

# Headers para evitar bloqueos básicos
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def extraer_descripcion(html):
    """
    Extrae la descripción desde:
    .startup-description .field__item
    """

    soup = BeautifulSoup(html, "html.parser")

    descripcion_div = soup.select_one(
        ".startup-description .field__item"
    )

    if descripcion_div:
        return descripcion_div.get_text(strip=True)

    return None


def procesar_startups(lista_resultados):
    """
    Recorre todas las startups y añade la descripción.
    """

    resultados_enriquecidos = []

    for item in lista_resultados:

        enlace = item.get("enlace")

        if not enlace:
            item["descripcion"] = None
            resultados_enriquecidos.append(item)
            continue

        # Construcción URL absoluta
        url = urljoin(BASE_URL, enlace)

        print(f"Procesando: {url}")

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=15
            )

            response.raise_for_status()

            descripcion = extraer_descripcion(response.text)

            item["descripcion"] = descripcion

        except requests.RequestException as e:
            print(f"Error en {url}: {e}")
            item["descripcion"] = None

        resultados_enriquecidos.append(item)

        # Pequeña pausa para no saturar el servidor
        time.sleep(1)

    return resultados_enriquecidos


if __name__ == "__main__":

    resultados_finales = procesar_startups(resultados)

    print(
        json.dumps(
            resultados_finales,
            indent=2,
            ensure_ascii=False
        )
    )
```

Ejemplo de salida:

```json
[
  {
    "empresa": "MediaForm",
    "node_id": "113",
    "enlace": "/startups/mediaform",
    "logo": "/sites/default/files/2025-08/MediaForm.png",
    "etiqueta": "Gaming",
    "etiqueta_url": "/taxonomy/term/12",
    "descripcion": "Estudio especializado en paisajes sonoros y diseño de audio artesanal para videojuegos, cine y contenidos digitales"
  }
]
```

Mejoras recomendadas para producción:

* Paralelizar con `concurrent.futures`
* Reintentos automáticos (`requests.Session` + `HTTPAdapter`)
* Exportación a CSV/JSON
* Cacheado
* Rotación de proxies
* Scraping asíncrono con `aiohttp`
* Soporte anti-bloqueo (`cloudscraper`)

Versión rápida con concurrencia (10x más veloz):

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
```

Si quieres, también puedo darte:

* versión async ultra rápida (`aiohttp`)
* versión con `Scrapy`
* versión que exporte directamente a Excel
* versión preparada para miles de URLs
* versión con Selenium para páginas dinámicas
* versión con logging profesional y reintentos automáticos.


---

Aquí tienes la versión completa y profesional del scraper, incluyendo:

* `descripcion`
* `descripcion_larga`
* `video_presentacion`
* `trabajadores`

  * `nombre`
  * `cargo`
  * `imagen`

Además:

* Convierte todas las URLs relativas en absolutas
* Maneja errores
* Limpia textos
* Devuelve estructuras JSON limpias
* Añade listas vacías si no existen trabajadores
* Añade `""` si no existe vídeo

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

# =========================================================
# CONFIGURACIÓN
# =========================================================

BASE_URL = "https://ejemplo.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

# =========================================================
# DATOS DE ENTRADA
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
# EXTRACCIÓN
# =========================================================

def extraer_descripcion(soup):

    elemento = soup.select_one(
        ".startup-description .field--name-field-descripcion .field__item"
    )

    if elemento:
        return limpiar_texto(elemento.get_text())

    return ""


def extraer_descripcion_larga(soup):

    elemento = soup.select_one(
        ".solution-section .field--name-field-solucion .field__item p"
    )

    if elemento:
        return limpiar_texto(elemento.get_text())

    return ""


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

        # =====================================
        # NOMBRE
        # =====================================

        nombre_el = bloque.select_one(
            ".trabajador-startup-nombre .field__item"
        )

        nombre = limpiar_texto(
            nombre_el.get_text()
        ) if nombre_el else ""

        # =====================================
        # CARGO
        # =====================================

        cargo_el = bloque.select_one(
            ".trabajador-startup-cargo .field__item"
        )

        cargo = limpiar_texto(
            cargo_el.get_text()
        ) if cargo_el else ""

        # =====================================
        # IMAGEN
        # =====================================

        imagen = ""

        img_el = bloque.select_one(
            ".trabajador-startup-imagen img"
        )

        if img_el:

            imagen_src = (
                img_el.get("src")
                or img_el.get("data-src")
            )

            imagen = url_absoluta(imagen_src)

        trabajadores.append({
            "nombre": nombre,
            "cargo": cargo,
            "imagen": imagen
        })

    return trabajadores


# =========================================================
# PROCESAMIENTO
# =========================================================

def procesar_startup(item):

    enlace = item.get("enlace")

    if not enlace:

        item["descripcion"] = ""
        item["descripcion_larga"] = ""
        item["video_presentacion"] = ""
        item["trabajadores"] = []

        return item

    url = urljoin(BASE_URL, enlace)

    print(f"Procesando: {url}")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # =====================================
        # EXTRACCIONES
        # =====================================

        item["descripcion"] = extraer_descripcion(soup)

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

    except requests.RequestException as e:

        print(f"Error en {url}: {e}")

        item["descripcion"] = ""
        item["descripcion_larga"] = ""
        item["video_presentacion"] = ""
        item["trabajadores"] = []

    return item


def procesar_startups(lista_resultados):

    resultados_enriquecidos = []

    for item in lista_resultados:

        startup = procesar_startup(item)

        resultados_enriquecidos.append(startup)

        # Evita saturar el servidor
        time.sleep(1)

    return resultados_enriquecidos


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    resultados_finales = procesar_startups(resultados)

    print(
        json.dumps(
            resultados_finales,
            indent=2,
            ensure_ascii=False
        )
    )
```

Ejemplo de salida final:

```json
[
  {
    "empresa": "MediaForm",
    "node_id": "113",
    "enlace": "/startups/mediaform",
    "logo": "https://ejemplo.com/sites/default/files/2025-08/MediaForm.png",
    "etiqueta": "Gaming",
    "etiqueta_url": "/taxonomy/term/12",
    "descripcion": "Estudio especializado en paisajes sonoros y diseño de audio artesanal para videojuegos, cine y contenidos digitales",
    "descripcion_larga": "Horizontal Tree es un estudio especializado en la creación de paisajes sonoros...",
    "video_presentacion": "https://ejemplo.com/sites/default/files/2025-08/Entrevista%20Horizontal%20Tree.MP4",
    "trabajadores": [
      {
        "nombre": "Antonio Blanca Rodríguez",
        "cargo": "Co-fundador",
        "imagen": ""
      },
      {
        "nombre": "Marcos David Cabrera Barranco",
        "cargo": "Co-fundador",
        "imagen": ""
      }
    ]
  }
]
```

Siguiente mejora recomendada para scraping masivo:

* `ThreadPoolExecutor` → 5-20x más rápido
* `requests.Session()` → reutiliza conexiones
* reintentos automáticos
* guardado incremental
* exportación directa a MongoDB/PostgreSQL
* scraping asíncrono (`aiohttp`)
* Selenium/Playwright si el contenido se carga dinámicamente.
