#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construye y valida el proyecto de App Inventor `PenalBot.aia`.

Pasos:
  1. Escribe Screen1.scm (disenador) a partir de la estructura declarada aqui.
  2. Copia las imagenes de assets/ al proyecto.
  3. Valida los bloques (.bky): XML, ids unicos, tipos de bloque y componentes.
  4. Empaqueta todo en appinventor/PenalBot.aia listo para importar.

Uso:  python3 herramientas/construir_aia.py
"""

import json
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROYECTO = "PenalBot"
PAQUETE = "appinventor.ai_alumno"
DIR_FUENTES = os.path.join(RAIZ, "appinventor", PROYECTO)
DIR_CODIGO = os.path.join(DIR_FUENTES, "src", "appinventor", "ai_alumno", PROYECTO)
RUTA_AIA = os.path.join(RAIZ, "appinventor", PROYECTO + ".aia")

# Version del formato de App Inventor usada al guardar el proyecto (nb2025/nb2026)
YA_VERSION = "237"
BLOCKS_LANGUAGE_VERSION = "39"

NS_MUTACION = "http://www.w3.org/1999/xhtml"


def propiedades_screen():
    """Estructura JSON del disenador (Screen1.scm)."""
    bola = {
        "$Name": "Bola",
        "$Type": "ImageSprite",
        "$Version": "11",
        "Enabled": "True",
        "Heading": "0",
        "Picture": "balon.png",
        "Speed": "0",
        "Visible": "True",
        "Width": "44",
        "Height": "44",
        "X": "150",
        "Y": "280",
        "Uuid": "-1487261934",
    }
    lienzo = {
        "$Name": "Lienzo1",
        "$Type": "Canvas",
        "$Version": "15",
        "BackgroundColor": "&HFF2E7D32",
        "BackgroundImage": "campo.png",
        "Height": "-2",
        "Width": "-2",
        "Uuid": "-1134976021",
        "$Components": [bola],
    }
    boton = {
        "$Name": "BtnReiniciar",
        "$Type": "Button",
        "$Version": "8",
        "BackgroundColor": "&HFF14532D",
        "FontSize": "15",
        "Height": "-1",
        "Width": "-1",
        "Shape": "1",
        "Text": "Reiniciar bal\u00f3n",
        "TextColor": "&HFFFFFFFF",
        "Uuid": "1437170182",
    }
    etiqueta_rebotes = {
        "$Name": "LblRebotes",
        "$Type": "Label",
        "$Version": "6",
        "FontSize": "16",
        "Height": "-1",
        "Width": "-1",
        "Text": "Rebotes: 0",
        "TextColor": "&HFFFFFFFF",
        "Uuid": "-771039852",
    }
    fila = {
        "$Name": "FilaInferior",
        "$Type": "HorizontalArrangement",
        "$Version": "4",
        "AlignHorizontal": "3",
        "AlignVertical": "2",
        "Height": "-1",
        "Width": "-2",
        "Uuid": "983091217",
        "$Components": [boton, etiqueta_rebotes],
    }
    titulo = {
        "$Name": "LblTitulo",
        "$Type": "Label",
        "$Version": "6",
        "BackgroundColor": "&HFF14532D",
        "FontBold": "True",
        "FontSize": "16",
        "Height": "-1",
        "Text": "Arrastra el bal\u00f3n para patearlo",
        "TextAlignment": "1",
        "TextColor": "&HFFFFFFFF",
        "Width": "-2",
        "Uuid": "-2017182364",
    }

    return {
        "authURL": ["ai2.appinventor.mit.edu"],
        "YaVersion": YA_VERSION,
        "Source": "Form",
        "Properties": {
            "$Name": "Screen1",
            "$Type": "Form",
            "$Version": "32",
            "AlignHorizontal": "3",
            "AppName": PROYECTO,
            "BackgroundColor": "&HFF0B2E0B",
            "ShowStatusBar": "True",
            "Sizing": "Responsive",
            "Theme": "Classic",
            "Title": "Penales LOBOS BUAP",
            "Uuid": "0",
            "$Components": [titulo, lienzo, fila],
        },
    }


def escribir_scm():
    ruta = os.path.join(DIR_CODIGO, "Screen1.scm")
    contenido = "#|\n$JSON\n" + json.dumps(propiedades_screen(), ensure_ascii=True,
                                            separators=(",", ":")) + "\n|#\n"
    escribir(ruta, contenido)
    return ruta


def escribir(ruta, contenido):
    directorio = os.path.dirname(ruta)
    if not os.path.isdir(directorio):
        os.makedirs(directorio)
    with open(ruta, "w", encoding="utf-8", newline="\n") as archivo:
        archivo.write(contenido)


def escribir_propiedades():
    ruta = os.path.join(DIR_FUENTES, "youngandroidproject", "project.properties")
    contenido = "\n".join([
        "main=%s.%s.Screen1" % (PAQUETE, PROYECTO),
        "name=%s" % PROYECTO,
        "assets=../assets",
        "source=../src",
        "build=../build",
        "versioncode=1",
        "versionname=1.0",
        "useslocation=False",
        "aname=%s" % PROYECTO,
        "sizing=Responsive",
        "showlistsasjson=True",
        "actionbar=False",
        "theme=Classic",
        "color.primary=&HFF14532D",
        "color.primary.dark=&HFF0B2E0B",
        "color.accent=&HFFFFC107",
        "",
    ])
    escribir(ruta, contenido)
    return ruta


def copiar_assets():
    destino = os.path.join(DIR_FUENTES, "assets")
    if not os.path.isdir(destino):
        os.makedirs(destino)
    for nombre in ("campo.png", "balon.png"):
        origen = os.path.join(RAIZ, "assets", nombre)
        if not os.path.isfile(origen):
            raise SystemExit("Falta la imagen %s (ejecuta generar_assets.py)" % origen)
        shutil.copyfile(origen, os.path.join(destino, nombre))
    return destino

# --------------------------------------------------------------------------
# Validacion
# --------------------------------------------------------------------------
TIPOS_BLOQUE = {
    "global_declaration", "lexical_variable_get", "lexical_variable_set",
    "math_number", "math_add", "math_subtract", "math_division",
    "logic_compare", "controls_if", "text", "text_join",
    "component_event", "component_method", "component_set_get",
}

EVENTOS_VALIDOS = {
    "Form": {"Initialize"},
    "ImageSprite": {"Flung", "EdgeReached", "Touched", "Dragged"},
    "Button": {"Click"},
    "Canvas": {"Touched", "Dragged"},
}

METODOS_VALIDOS = {
    "ImageSprite": {"MoveTo", "Bounce", "PointInDirection"},
}

PROPIEDADES_VALIDAS = {
    "ImageSprite": {"Heading", "Speed", "X", "Y", "Visible", "Enabled"},
    "Canvas": {"Width", "Height", "BackgroundImage"},
    "Label": {"Text", "TextColor", "FontSize"},
    "Form": {"Title", "BackgroundColor"},
}


def _componentes(scm):
    encontrados = []

    def recorrer(propiedades):
        for componente in propiedades.get("$Components", []):
            encontrados.append(componente)
            recorrer(componente)

    recorrer(scm["Properties"])
    return encontrados


def validar():
    print("Validando proyecto...")
    ruta_scm = os.path.join(DIR_CODIGO, "Screen1.scm")
    ruta_bky = os.path.join(DIR_CODIGO, "Screen1.bky")

    with open(ruta_scm, encoding="utf-8") as archivo:
        texto = archivo.read()
    assert texto.startswith("#|\n$JSON\n") and texto.rstrip().endswith("|#"), \
        "Screen1.scm no tiene el formato #| $JSON |#"
    scm = json.loads(texto.split("$JSON", 1)[1].rsplit("|#", 1)[0])
    assert scm["YaVersion"] == YA_VERSION

    componentes = {c["$Name"]: c for c in _componentes(scm)}
    componentes["Screen1"] = scm["Properties"]

    # Los archivos de imagen referenciados deben existir
    for componente in componentes.values():
        for clave in ("BackgroundImage", "Picture", "Icon"):
            valor = componente.get(clave, "")
            if valor:
                ruta = os.path.join(DIR_FUENTES, "assets", valor)
                assert os.path.isfile(ruta), "No existe el asset %s" % valor

    arbol = ET.parse(ruta_bky)
    raiz = arbol.getroot()
    assert raiz.tag.endswith("xml")

    ids = []
    for bloque in raiz.iter():
        if bloque.tag.endswith("block"):
            tipo = bloque.get("type")
            assert tipo in TIPOS_BLOQUE, "Tipo de bloque desconocido: %s" % tipo
            ids.append(bloque.get("id"))

            if tipo in ("component_event", "component_method", "component_set_get"):
                mutacion = None
                for hijo in bloque:
                    if hijo.tag.endswith("mutation"):
                        mutacion = hijo
                assert mutacion is not None, "Bloque %s sin mutation" % tipo
                instancia = mutacion.get("instance_name")
                assert instancia in componentes, \
                    "El bloque usa un componente inexistente: %s" % instancia
                tipo_componente = componentes[instancia]["$Type"]

                if tipo == "component_event":
                    evento = mutacion.get("event_name")
                    assert evento in EVENTOS_VALIDOS.get(tipo_componente, set()), \
                        "Evento %s invalido para %s" % (evento, tipo_componente)
                    tiene_do = any(hijo.tag.endswith("statement") for hijo in bloque)
                    assert tiene_do, \
                        "El evento %s no tiene bloque DO" % evento
                elif tipo == "component_method":
                    metodo = mutacion.get("method_name")
                    assert metodo in METODOS_VALIDOS.get(tipo_componente, set()), \
                        "Metodo %s invalido para %s" % (metodo, tipo_componente)
                else:
                    prop = mutacion.get("property_name")
                    assert prop in PROPIEDADES_VALIDAS.get(tipo_componente, set()), \
                        "Propiedad %s invalida para %s" % (prop, tipo_componente)
                    # La propiedad tambien debe aparecer como campo PROP
                    campos = [f.text for f in bloque if f.tag.endswith("field")]
                    assert prop in campos, "Falta el campo PROP en %s" % prop

    assert len(ids) == len(set(ids)), "Hay ids de bloque repetidos"

    # Variables declaradas vs usadas
    declaradas = set()
    usadas = set()
    for bloque in raiz.iter():
        if not bloque.tag.endswith("block"):
            continue
        if bloque.get("type") == "global_declaration":
            for campo in bloque:
                if campo.tag.endswith("field") and campo.get("name") == "NAME":
                    declaradas.add("global " + campo.text)
        for campo in bloque:
            if campo.tag.endswith("field") and campo.get("name") == "VAR":
                usadas.add(campo.text)
    faltantes = {v for v in usadas if v.startswith("global ") and v not in declaradas}
    assert not faltantes, "Variables globales sin declarar: %s" % faltantes

    print("  OK: %d bloques, %d componentes, %d assets" % (
        len(ids), len(componentes), len(os.listdir(os.path.join(DIR_FUENTES, "assets")))))


# --------------------------------------------------------------------------
# Empaquetado .aia
# --------------------------------------------------------------------------
def empaquetar():
    if os.path.exists(RUTA_AIA):
        os.remove(RUTA_AIA)
    archivos = []
    for base, _, nombres in os.walk(DIR_FUENTES):
        for nombre in nombres:
            if nombre.endswith(".aia") or nombre.endswith(".pyc"):
                continue
            completo = os.path.join(base, nombre)
            relativo = os.path.relpath(completo, DIR_FUENTES).replace(os.sep, "/")
            archivos.append((relativo, completo))
    archivos.sort()
    with zipfile.ZipFile(RUTA_AIA, "w", zipfile.ZIP_DEFLATED) as zf:
        for relativo, completo in archivos:
            zf.write(completo, relativo)
    return RUTA_AIA, archivos


def main():
    escribir_propiedades()
    escribir_scm()
    copiar_assets()
    validar()
    ruta, archivos = empaquetar()
    print("Empaquetado: %s (%d archivos, %d bytes)" % (
        os.path.relpath(ruta, RAIZ), len(archivos), os.path.getsize(ruta)))
    for relativo, _ in archivos:
        print("   ", relativo)


if __name__ == "__main__":
    main()
