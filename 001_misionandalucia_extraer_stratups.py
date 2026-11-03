#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  @Name: 001_misionandalucia_extraer_stratups.py
  @Author: fcarbajo
  @Site: 
  @Descripción: Script para la extarcción de Startups de Misión Andalucía (basado en BeautifulSoup).
  @Usage:
    python 001_misionandalucia_extraer_stratups.py [fichero_html_noticias]
"""

__author__ = 'Fernando J. Carbajo'
__version__ = '1.0.5'
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
_DBG = True

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

import helper as hlp
import helper_pd as hpd
import coloriza as cl

#import argparse
import requests
from urllib.parse import urljoin
import warnings
from bs4 import BeautifulSoup
from lxml import html
import json
import yaml
from tqdm import tqdm

# Funciones auxiliares
def limpiar_texto(texto):
  """
  Limpia espacios y saltos de línea innecesarios.
  """
  if not texto:
    return None

  return " ".join(texto.split())


def download_file(enlace, fichero='fichero', tipo='csv', cookies=None):

  requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecurePlatformWarning)
  requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

  cl.cout_pair("  Fichero: ", fichero)
  if _debug:
    cl.print_dbg("    URL:", enlace)

  if cookies:
    for cookie in cookies:
      s.cookies.set(cookie['name'], cookie['value'])
    s = requests.Session()
    respuesta = s.get(enlace, verify=False).content
  else:
    respuesta = requests.get(enlace, headers=headers, verify=False).content

  if respuesta:
    with open(fichero, 'wb') as f:
      f.write(respuesta)
      f.close()

  print("  {}".format(cl.ctext("-- Descarga completa --", cl.Fore.CYAN)))

  return fichero

def list_results(lista_resultados):

  for i, resultado in enumerate(lista_resultados, 1):
    cl.cout_pair("  Startup ", i)
    cl.cout_pair("   Nombre: ", resultado['startup'])
    cl.cout_pair("   Node Id: ", resultado['node_id'])
    cl.cout_pair("   Enlace detalle: ", resultado['enlace_drupal'])
    cl.cout_pair("   Logo: ", resultado['logo'])
    cl.cout_pair("   Catregoría: ", resultado['etiqueta'])
    cl.cout_pair("   Catregoría url: ", resultado['etiqueta_url'])
    cl.cout_pair("   Web: ", resultado['web'])
    print("  {}".format("-" * 80))

def fetch_html(origen):
  """
    Obtiene el HTML desde una URL o desde un fichero local.
   """
  try:
    if os.path.isfile(origen):
      with open(origen, 'r', encoding='utf-8') as file:
        return file.read()

    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecurePlatformWarning)
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Hacemos la petición HTTP
    response = requests.get(origen, headers=headers, verify=False, timeout=10)
    response.raise_for_status()  # Lanza error si falla la petición
    response.encoding = 'utf-8'
    return response.text
  except Exception as e:
    print(f"Error al cargar el HTML: {e}", file=sys.stderr)
    return None


def extraer_datos_startups(list_startups):
  """
  """

  total = len(list_startups)
  cl.cout_pair("\n   Startups: ", total)

  for item in tqdm(list_startups, total=total, desc="Procesando startups", unit="startup"):
    url_extraccion = f"{url_base}/{item['enlace_drupal']}"
    html_src = fetch_html(url_extraccion)
    soup = BeautifulSoup(html_src, "html.parser")

    # Seleccionamos por estilos
    descripcion_div = soup.select_one(".startup-description .field__item")
    desc_corta = descripcion_div.get_text(strip=True) if descripcion_div else ""

    descripcion_div = soup.select_one(".solution-section .field__item p")
    desc_larga = limpiar_texto(descripcion_div.get_text())
    
    video_src = soup.select_one(".video-container video source")
    video = video_src.get("src") if video_src else ""

    empresa_link = soup.select_one("a.btn-startup-cta")
    empresa_url =  empresa_link.get("href") if empresa_link else ""
    if not empresa_url:
      empresa_link = soup.select_one("a.link-startup-cta")
      empresa_url =  empresa_link.get("href") if empresa_link else ""

    bloques = soup.select(".trabajador-startup-content")
    trabajadores = []
    for bloque in bloques:
      trabajador_nombre = bloque.select_one(".trabajador-startup-nombre .field__item")
      nombre = limpiar_texto(trabajador_nombre.get_text()) if trabajador_nombre else ""

      trabajador_cargo = bloque.select_one(".trabajador-startup-cargo .field__item")
      cargo = limpiar_texto(trabajador_cargo.get_text()) if trabajador_cargo else ""

      trabajador_img = bloque.select_one(".trabajador-startup-imagen img")
      imagen = trabajador_img.get("src") or trabajador_img.get("data-src") if trabajador_img else ""

      trabajador_link = bloque.select_one("a.linkedin-link")
      linkedin = trabajador_link.get("href") if trabajador_link else ""

      trabajadores.append({
              "nombre": nombre,
              "cargo": cargo,
              "linkedin": linkedin,
              "imagen": imagen
          })

    item.setdefault("descripcion", desc_corta)
    item.setdefault("descripcion_larga", desc_larga)
    item.setdefault("video", video)
    item.setdefault("web", empresa_url)
    item.setdefault("trabajadores", trabajadores if trabajadores else [])

  return list_startups


def parse_bs4_startups(html_str: str):
  """
  Extrae las startups desde el HTML usando BeautifulSoup.
  Sitio: https://misionandalucia.es

  Startups: /startups
    Lista tarjetas Startups: //div[@id="views-bootstrap-vista-startups-block-1"]
      Tarjeta: //article
      Etiqueta: //span[contains(@class, 'field__item tag-')]/a
      Logo: //div[@class="startup-teaser-logo"]/img
      Nombre: //div[@class="startup-teaser-name"]/a

  """
  soup = BeautifulSoup(html_str, "lxml")

  empresas = []
  container = soup.find("div", id="views-bootstrap-vista-startups-block-1")

  if not container:
    print("[ERROR] No se encontró el contenedor principal")
    return []

  startups = container.find_all("article")
  for startup in startups:
    try:
      node_id = startup.get("data-history-node-id")
      startup_name = startup.select_one("div.startup-teaser-name a")
      empresa = startup_name.get_text(strip=True) if startup_name else ""
      empresa_detalle = startup_name.get("href") if startup_name else ""

      logo_url = startup.select_one("div.startup-teaser-logo img")
      logo = logo_url.get("src") if logo_url else ""

      tag_name = startup.select_one("span[class*='field__item tag-'] a")
      etiqueta = tag_name.get_text(strip=True) if tag_name else ""
      etiqueta_url =  tag_name.get("href") if tag_name else ""
  
      # Guardamos en una lista
      empresas.append({
          "startup": empresa,
          "node_id": node_id,
          "enlace_drupal": empresa_detalle,
          "logo": logo,
          "etiqueta": etiqueta,
          "etiqueta_url": etiqueta_url
      })
    except Exception as e:
      print(f"Error procesando una entrada: {e}")
      continue

  lst_sorted = sorted(empresas, key=lambda x: int(x['node_id']), reverse=False)

  return lst_sorted


def save_to_files(elements, filename="startups"):
  """
  Guarda los eventos en ficheros JSON y YAML
  """
  try:
    json_file = f"{filename}.json"
    with open(f"{path_out}\\{json_file}", "w", encoding="utf-8") as f_json:
      json.dump(elements, f_json, ensure_ascii=False, indent=2)

    yaml_file = f"{filename}.yaml"
    with open(f"{path_out}\\{yaml_file}", "w", encoding="utf-8") as f_yaml:
      yaml.dump(elements, f_yaml, allow_unicode=True, sort_keys=False)

    print(f"\n  {cl.ctext('Datos generados:')}")
    print(f"    {cl.ctext(json_file, cl.Fore.YELLOW)}")
    print(f"    {cl.ctext(yaml_file, cl.Fore.YELLOW)}")
  except Exception as e:
    print(f"Error al guardar los archivos:\n  -> {e}")


def main():
  parser = argparse.ArgumentParser(description="Extractor de Startups de Misión Andalucía")
  parser.add_argument("source", help="URL de la página o fichero local con HTML")
  parser.add_argument("--out", default="startups", help="Archivo de salida (JSON y YAML)")

  args = parser.parse_args()

  html_content = fetch_html(args.source)
  events = parse_events(html_content)
  #save_to_files(events, args.json, args.yaml)
  save_to_files(events, args.out)


if __name__ == '__main__':

  if py_version < 3:
    version = "%s.%s.%s" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    print("Se requiere Python 3, la versión actual es %s" % (version))
    sys.exit(1)

  print(f"Python: {py_full_version}\n")
  
  #origen = sys.argv[1] if len(sys.argv) > 1 else "https://misionandalucia.es/startups"

  # Carga de configuración.
  #cfg = hlp.config('hgp-incurridos.ini')
  #_debug = hlp.config_dbg(cfg, section='aplicacion', option='debug')

  headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
  }

  # Marca temporal del nombre de ficheros
  fecha = hlp.get_fecha_hm() #datetime.now().strftime("%Y%m%d")
  
  organismo = "misionandalucia"
  organismo_abrev = "ma"
  url_base = "https://misionandalucia.es"
  url_extraccion = f"{url_base}/startups"
  cl.cout_pair("  URL: ", url_extraccion)
  cl.cout_pair("  Marca temporal: ", fecha)

  nfichero = f"001-{organismo}-starups"
  if fecha == None:
    nfichero = hlp.gen_file_name_timestamp(nfichero)
  else:
    nfichero = "%s-%s" % (nfichero, fecha)
  cl.cout_pair("  Fichero salida: ", nfichero)

  ##download_file()
  # Obtener el contenido web desde fichero (Depuración)
  html_text = fetch_html(url_extraccion)
  #html_text = fetch_html(f'{path_in}\\{organismo}-noticias.html')

  lista_resultados = parse_bs4_startups(html_text)
  lista_resultados2 = extraer_datos_startups(lista_resultados)
  save_to_files(lista_resultados2, nfichero)
  list_results(lista_resultados2)
