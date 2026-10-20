#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica un archivo .aia ya construido, sin abrir App Inventor.

Comprueba:
  * que el ZIP tenga las entradas obligatorias (project.properties, .scm, .bky),
  * que `main` de project.properties coincida con la ruta del .scm,
  * que el disenador (.scm) sea JSON valido con YaVersion y componentes,
  * que las imagenes referenciadas esten dentro del paquete y sean PNG validos,
  * que los bloques (.bky) sean XML valido y que el bloque yacodeblocks declare
    la misma version de App Inventor.

Uso:  python3 herramientas/verificar_aia.py [ruta.aia]
"""

import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_AIA = os.path.join(RAIZ, "appinventor", "PenalBot.aia")


def verificar(ruta_aia):
    print("Verificando %s ..." % os.path.relpath(ruta_aia, RAIZ))
    errores = []

    with zipfile.ZipFile(ruta_aia) as zf:
        nombres = zf.namelist()
        if "youngandroidproject/project.properties" not in nombres:
            errores.append("falta youngandroidproject/project.properties")
        scm = [n for n in nombres if n.endswith(".scm")]
        bky = [n for n in nombres if n.endswith(".bky")]
        if len(scm) != 1:
            errores.append("se esperaba un .scm, hay %d" % len(scm))
        if len(bky) != 1:
            errores.append("se esperaba un .bky, hay %d" % len(bky))

        propiedades = zf.read("youngandroidproject/project.properties").decode("utf-8")
        valores = dict(
            linea.split("=", 1) for linea in propiedades.splitlines() if "=" in linea)
        esperado = scm[0][:-4].replace("/", ".")
        if esperado.startswith("src."):
            esperado = esperado[len("src."):]
        if valores.get("main") != esperado:
            errores.append("main (%s) no coincide con el .scm (%s)" % (
                valores.get("main"), esperado))

        texto_scm = zf.read(scm[0]).decode("utf-8")
        if not (texto_scm.startswith("#|") and "$JSON" in texto_scm):
            errores.append("el .scm no tiene el envoltorio #| $JSON")
        datos = json.loads(texto_scm.split("$JSON", 1)[1].rsplit("|#", 1)[0])
        if "YaVersion" not in datos or "Properties" not in datos:
            errores.append("el .scm no tiene YaVersion/Properties")
        if datos["Properties"].get("$Type") != "Form":
            errores.append("el .scm no describe un Form")

        componentes = []

        def recorrer(props):
            for componente in props.get("$Components", []):
                componentes.append(componente)
                recorrer(componente)

        recorrer(datos["Properties"])
        nombres_componentes = [c["$Name"] for c in componentes]
        for obligatorio in ("Canvas", "ImageSprite"):
            tipos = [c["$Type"] for c in componentes]
            if obligatorio not in tipos:
                errores.append("no hay ningun componente %s" % obligatorio)

        # Imagenes referenciadas
        for componente in componentes:
            for clave in ("BackgroundImage", "Picture", "Icon"):
                nombre = componente.get(clave)
                if not nombre:
                    continue
                ruta = "assets/" + nombre
                if ruta not in nombres:
                    errores.append("imagen referenciada inexistente: %s" % ruta)
                    continue
                cabecera = zf.read(ruta)[:24]
                if cabecera[:8] != b"\x89PNG\r\n\x1a\n":
                    errores.append("%s no es un PNG" % ruta)
                    continue
                ancho, alto = struct.unpack(">II", cabecera[16:24])
                print("    %s: %dx%d px" % (ruta, ancho, alto))

        arbol = ET.fromstring(zf.read(bky[0]).decode("utf-8"))
        bloques = [b for b in arbol.iter() if b.tag.endswith("block")]
        version = None
        for hijo in arbol:
            if hijo.tag.endswith("yacodeblocks"):
                version = hijo.get("ya-version")
                idioma = hijo.get("language-version")
                if version != datos["YaVersion"]:
                    errores.append("ya-version (%s) distinto de YaVersion (%s)" % (
                        version, datos["YaVersion"]))
                if not idioma:
                    errores.append("falta language-version en yacodeblocks")
        if version is None:
            errores.append("falta el bloque yacodeblocks")
        ids = [b.get("id") for b in bloques]
        if len(ids) != len(set(ids)):
            errores.append("ids de bloque repetidos")

    print("    componentes: %s" % ", ".join(nombres_componentes))
    print("    bloques: %d" % len(bloques))

    if errores:
        print("\nERRORES:")
        for error in errores:
            print("  -", error)
        return 1
    print("\nOK: el paquete .aia es consistente.")
    return 0


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_AIA
    if not os.path.isfile(ruta):
        print("No existe %s (ejecuta construir_aia.py)" % ruta)
        return 2
    return verificar(ruta)


if __name__ == "__main__":
    sys.exit(main())
