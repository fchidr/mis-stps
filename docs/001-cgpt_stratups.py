#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  @Name: 001-cgpt_stratups.py
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
