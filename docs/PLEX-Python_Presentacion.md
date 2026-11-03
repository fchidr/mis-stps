<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Actuando como un experto programador en Python, diseña el código necesario para incluir una barra de progreso en línea de comandos para hacer el seguimiento de un bucle de extracción de datos de una lista de páginas. EL código para el procesado de las páginas es:

def extraer_datos_startups(list_startups):
"""
"""

for item in list_startups:

    url_extraccion = f"{url_base}/{item['enlace_drupal']}"
    html_src = fetch_html(url_extraccion)
    soup = BeautifulSoup(html_src, "html.parser")
    
    #container = soup.find("section", class_="content")
    #print(f"container:\\n{container}")
    
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

La forma más simple y robusta es envolver el `for` con `tqdm`, que está pensado precisamente para mostrar una barra de progreso en loops de Python y se integra bien con la consola CLI.[^1_1]
Aquí tienes tu función adaptada para que muestre avance, tiempo estimado y cantidad procesada.[^1_1]

## Código propuesto

```python
from tqdm import tqdm
from bs4 import BeautifulSoup

def extraer_datos_startups(list_startups):
    """
    Extrae datos de una lista de startups mostrando una barra de progreso en consola.
    """

    total = len(list_startups)

    for item in tqdm(list_startups, total=total, desc="Extrayendo startups", unit="startup"):
        url_extraccion = f"{url_base}/{item['enlace_drupal']}"
        html_src = fetch_html(url_extraccion)
        soup = BeautifulSoup(html_src, "html.parser")

        descripcion_div = soup.select_one(".startup-description .field__item")
        desc_corta = descripcion_div.get_text(strip=True) if descripcion_div else ""

        descripcion_div = soup.select_one(".solution-section .field__item p")
        desc_larga = limpiar_texto(descripcion_div.get_text()) if descripcion_div else ""

        video_src = soup.select_one(".video-container video source")
        video = video_src.get("src") if video_src else ""

        empresa_link = soup.select_one("a.btn-startup-cta")
        empresa_url = empresa_link.get("href") if empresa_link else ""
        if not empresa_url:
            empresa_link = soup.select_one("a.link-startup-cta")
            empresa_url = empresa_link.get("href") if empresa_link else ""

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
```


## Instalación

Si no lo tienes instalado:

```bash
pip install tqdm
```

`tqdm` recomienda precisamente envolver cualquier iterable con `tqdm(iterable)` para obtener una barra de progreso rápida y con sobrecarga muy baja.[^1_1]

## Variante con contador manual

Si prefieres controlar tú el texto que se muestra, también puedes iterar con índice:

```python
from tqdm import tqdm

for i, item in enumerate(tqdm(list_startups, desc="Extrayendo startups", unit="startup"), 1):
    ...
```


## Recomendaciones prácticas

- Usa `desc` para identificar la tarea.
- Usa `unit="startup"` para que la barra muestre la unidad procesada.
- Si el proceso puede fallar en alguna página, conviene envolver cada iteración en `try/except` para que la barra siga avanzando aunque una extracción dé error.
- Si quieres una salida más elegante o con colores, `rich` también ofrece barras de progreso en terminal.[^1_2]

Una mejora útil sería añadir manejo de errores por página y guardar los fallos sin detener todo el proceso.
<span style="display:none">[^1_10][^1_3][^1_4][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://tqdm.github.io

[^1_2]: https://rich.readthedocs.io/en/stable/reference/progress_bar.html

[^1_3]: https://www.youtube.com/watch?v=jx0r-lHOWW8

[^1_4]: https://stackoverflow.com/questions/70797007/progress-bar-in-python-using-rich

[^1_5]: https://www.reddit.com/r/learnpython/comments/v1scb8/terminal_progress_bar_help_python/

[^1_6]: https://calmcode.io/course/tqdm/making-a-progress-bar

[^1_7]: https://www.instagram.com/p/DGfat_JzjN7/

[^1_8]: https://www.geeksforgeeks.org/python/progress-bars-in-python/

[^1_9]: https://www.datacamp.com/tutorial/progress-bars-in-python

[^1_10]: https://github.com/tqdm/tqdm

Seguimientos
Cómo implementar manejo de excepciones sin detener el bucle tqdm
Personalizar colores y formato de barra de progreso con librería Rich
Guardar fallos de scraping en un log durante la ejecución del bucle
Diferencias de rendimiento entre tqdm y barras de progreso de Rich
Cómo guardar los datos extraídos progresivamente en un archivo CSV

---

# Detállame una versión que personalice colores y formato de barra de progreso con librería Rich, y la implementación con manejo de errores sin detener el bucle.

Ordena la lista por el dato denominado 'node_id' que es un entero almacenado como cadena

Aquí tienes una versión más completa usando **Rich** para personalizar colores y formato, ordenar por `node_id` como entero y continuar aunque alguna página falle.[^2_1][^2_2]
La idea es: ordenar primero la lista, crear una barra con columnas personalizadas y envolver cada extracción en `try/except` para registrar errores sin detener el bucle.[^2_2][^2_1]

## Código con Rich

```python
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    SpinnerColumn,
)
from rich.style import Style

console = Console()

def extraer_datos_startups(list_startups):
    """
    Extrae datos de startups mostrando progreso con Rich.
    Ordena por node_id numérico aunque venga como cadena.
    No detiene el proceso si una página falla.
    """

    list_startups = sorted(
        list_startups,
        key=lambda x: int(x.get("node_id", 0))
    )

    errores = []

    progress = Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(
            bar_width=None,
            complete_style=Style(color="green"),
            finished_style=Style(color="green", bold=True),
            pulse_style=Style(color="magenta"),
            style=Style(color="grey37"),
        ),
        MofNCompleteColumn(),
        TextColumn("[bold yellow]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
        expand=True,
    )

    with progress:
        task = progress.add_task(
            "[green]Extrayendo startups",
            total=len(list_startups)
        )

        for item in list_startups:
            try:
                url_extraccion = f"{url_base}/{item['enlace_drupal']}"
                html_src = fetch_html(url_extraccion)
                soup = BeautifulSoup(html_src, "html.parser")

                descripcion_div = soup.select_one(".startup-description .field__item")
                desc_corta = descripcion_div.get_text(strip=True) if descripcion_div else ""

                descripcion_div = soup.select_one(".solution-section .field__item p")
                desc_larga = limpiar_texto(descripcion_div.get_text()) if descripcion_div else ""

                video_src = soup.select_one(".video-container video source")
                video = video_src.get("src") if video_src else ""

                empresa_link = soup.select_one("a.btn-startup-cta")
                empresa_url = empresa_link.get("href") if empresa_link else ""
                if not empresa_url:
                    empresa_link = soup.select_one("a.link-startup-cta")
                    empresa_url = empresa_link.get("href") if empresa_link else ""

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

            except Exception as e:
                errores.append({
                    "node_id": item.get("node_id"),
                    "enlace_drupal": item.get("enlace_drupal"),
                    "error": str(e)
                })
                console.print(
                    f"[bold red]Error[/bold red] en node_id={item.get('node_id')}: {e}"
                )
            finally:
                progress.update(task, advance=1)

    return list_startups, errores
```


## Qué cambia

La barra de progreso usa `SpinnerColumn`, `TextColumn`, `BarColumn`, `MofNCompleteColumn`, `TimeElapsedColumn` y `TimeRemainingColumn`, que son columnas estándar de Rich para construir displays más ricos y legibles.[^2_1]
Los estilos se personalizan con `complete_style`, `finished_style`, `pulse_style` y `style`, lo que permite cambiar colores del avance, del estado final y del fondo de la barra.[^2_3]
El orden se fuerza con `sorted(..., key=lambda x: int(x.get("node_id", 0)))`, convirtiendo `node_id` a entero aunque venga como texto.[^2_2]
El `try/except` captura fallos por página y el `finally` asegura que la barra avance incluso si una extracción falla.[^2_1]

## Variante más limpia con helper

Si quieres separar responsabilidades, puedes extraer la lógica de una página a una función auxiliar:

```python
def extraer_datos_item(item):
    url_extraccion = f"{url_base}/{item['enlace_drupal']}"
    html_src = fetch_html(url_extraccion)
    soup = BeautifulSoup(html_src, "html.parser")

    descripcion_div = soup.select_one(".startup-description .field__item")
    desc_corta = descripcion_div.get_text(strip=True) if descripcion_div else ""

    descripcion_div = soup.select_one(".solution-section .field__item p")
    desc_larga = limpiar_texto(descripcion_div.get_text()) if descripcion_div else ""

    video_src = soup.select_one(".video-container video source")
    video = video_src.get("src") if video_src else ""

    empresa_link = soup.select_one("a.btn-startup-cta")
    empresa_url = empresa_link.get("href") if empresa_link else ""
    if not empresa_url:
        empresa_link = soup.select_one("a.link-startup-cta")
        empresa_url = empresa_link.get("href") if empresa_link else ""

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

    return item
```

Y luego:

```python
def extraer_datos_startups(list_startups):
    list_startups = sorted(list_startups, key=lambda x: int(x.get("node_id", 0)))
    errores = []

    progress = Progress(
        SpinnerColumn(style="bold magenta"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green", pulse_style="magenta"),
        MofNCompleteColumn(),
        TextColumn("[bold yellow]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )

    with progress:
        task = progress.add_task("Extrayendo startups", total=len(list_startups))
        for item in list_startups:
            try:
                extraer_datos_item(item)
            except Exception as e:
                errores.append({"node_id": item.get("node_id"), "error": str(e)})
                console.print(f"[red]Error[/red] node_id={item.get('node_id')}: {e}")
            finally:
                progress.update(task, advance=1)

    return list_startups, errores
```


## Recomendaciones

Si `node_id` puede venir vacío o con valores no numéricos, conviene proteger la conversión con una función auxiliar para evitar que el `sorted()` falle.[^2_2]
También es buena idea registrar errores en una lista o archivo, porque imprimirlos en consola puede ser suficiente para depurar, pero no para auditoría posterior.[^2_1]
Rich permite displays vivos con `Live` y progreso personalizado, así que esta solución escala bien si luego quieres añadir una tabla de estadísticas o un panel de estado.[^2_1]

Una siguiente mejora útil sería convertir esto en una versión que además guarde los errores en un CSV aparte.
<span style="display:none">[^2_10][^2_4][^2_5][^2_6][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://rich.readthedocs.io/en/latest/live.html

[^2_2]: https://docs.python.org/3/howto/sorting.html

[^2_3]: https://rich.readthedocs.io/en/stable/reference/progress_bar.html

[^2_4]: https://timothygebhard.de/posts/richer-progress-bars-for-rich/

[^2_5]: https://www.geeksforgeeks.org/python/python-sorted-function/

[^2_6]: https://github.com/Textualize/rich/discussions/950

[^2_7]: https://github.com/Textualize/rich/discussions/482

[^2_8]: https://github.com/Textualize/rich/discussions/1114

[^2_9]: https://github.com/Textualize/rich/discussions/1130

[^2_10]: https://docs.python.org/es/3/howto/sorting.html

Seguimientos
Exportar los errores capturados a un archivo CSV organizado
Crear una tabla resumen con Rich tras completar el bucle
Usar Live displays para mostrar estadísticas en tiempo real
Integrar un log de eventos con Rich Console logging
Añadir reintentos automáticos con la librería Tenacity

---
