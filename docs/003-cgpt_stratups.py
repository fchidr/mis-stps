#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  @Name: 003-cgpt_stratups.py
  @Author: fcarbajo
  @Site: 
  @Descripción: Script para la extarcción de Startups de Misión Andalucía.
  @Usage:
  python 001-cgpt_stratups.py
"""

__author__ = 'Fernando J. Carbajo'
__version__ = '1.0.0'
__date__ = '2026-05-19'

import os
import sys
from pathlib import Path

script_path = os.path.dirname(os.path.abspath(__file__))
script_base = Path(script_path).parent
script_libs = f"{script_path}\\libs"
# La librería común está en el directorio Scripts de la raiz del proyecto
common_libs = f"{script_base.parent.parent}\\Scripts\\.pylibs"
path_in = f"{script_path}\\data"
path_out = f"{script_path}\\data"
PYTHON_PROFILE = os.environ['PYTHON_PROFILE']
PY_NAME = (os.environ['PY_NAME'])

py_full_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
py_version = sys.version_info.major
_DBG = False

if _DBG:
  print(f"\n  Python: {py_full_version}")
  print(f"  Profile: {PYTHON_PROFILE}")
  print(f"  Python name: {PY_NAME}")
  print(f"  Python name profile: {PY_NAME}")
  print(f"\n  script_path: {script_path}")
  print(f"  script_base: {script_base}")
  print(f"  script_libs: {script_libs}")
  print(f"  common_libs: {common_libs}")
  print(f"\n  Directorio entrada: {path_in}")
  print(f"  Directorio salida: {path_out}")

sys.path.insert(0, script_libs)
sys.path.insert(1, common_libs)

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
