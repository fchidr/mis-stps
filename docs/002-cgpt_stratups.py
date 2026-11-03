#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  @Name: 002-cgpt_stratups.py
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
#   "http": "http://user:password@proxyhost:port",
#   "https": "http://user:password@proxyhost:port",
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