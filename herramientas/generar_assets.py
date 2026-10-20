#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera las imagenes que usa el proyecto de App Inventor:

    assets/campo.png  -> cancha de futbol (vertical, franjas verdes y lineas blancas)
    assets/balon.png  -> balon blanco y negro con fondo transparente

No necesita librerias externas: el PNG se escribe a mano con zlib + struct.
Uso:  python3 herramientas/generar_assets.py
"""

import math
import os
import struct
import zlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ASSETS = os.path.join(RAIZ, "assets")


# --------------------------------------------------------------------------
# Escritura de archivos PNG (RGBA, 8 bits por canal)
# --------------------------------------------------------------------------
def escribir_png(ruta, ancho, alto, pixeles):
    """Escribe un buffer RGBA (bytearray de ancho*alto*4) como PNG."""

    def trozo(tipo, datos):
        return (struct.pack(">I", len(datos)) + tipo + datos +
                struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))

    crudo = bytearray()
    fila = ancho * 4
    for y in range(alto):
        crudo.append(0)  # filtro "None" de cada scanline
        crudo += pixeles[y * fila:(y + 1) * fila]

    cabecera = struct.pack(">IIBBBBB", ancho, alto, 8, 6, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" +
           trozo(b"IHDR", cabecera) +
           trozo(b"IDAT", zlib.compress(bytes(crudo), 9)) +
           trozo(b"IEND", b""))

    with open(ruta, "wb") as archivo:
        archivo.write(png)
    print("  escrito %s (%dx%d, %d bytes)" % (ruta, ancho, alto, len(png)))


def _cobertura(distancia, radio):
    """Cobertura suave para bordes antialias."""
    return max(0.0, min(1.0, radio + 0.5 - distancia))


def _dist_segmento(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    largo2 = dx * dx + dy * dy
    if largo2 == 0.0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / largo2
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _dentro(puntos, n, x, y):
    dentro = False
    j = n - 1
    for i in range(n):
        xi, yi = puntos[i]
        xj, yj = puntos[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            dentro = not dentro
        j = i
    return dentro

# --------------------------------------------------------------------------
# Lienzo con mezcla alfa y utilidades de dibujo
# --------------------------------------------------------------------------
class Lienzo(object):
    def __init__(self, ancho, alto, fondo=(0, 0, 0, 0)):
        self.ancho = ancho
        self.alto = alto
        self.px = bytearray(bytes(fondo) * (ancho * alto))

    def mezclar(self, x, y, rgb, cobertura):
        """Mezcla el color rgb con la cobertura (0..1) sobre el pixel x,y."""
        if cobertura <= 0.0:
            return
        if cobertura > 1.0:
            cobertura = 1.0
        i = (y * self.ancho + x) * 4
        px = self.px
        destino_alfa = px[i + 3] / 255.0
        alfa = cobertura + destino_alfa * (1.0 - cobertura)
        if alfa <= 0.0:
            px[i] = px[i + 1] = px[i + 2] = px[i + 3] = 0
            return
        for k in range(3):
            px[i + k] = int((rgb[k] * cobertura +
                             px[i + k] * destino_alfa * (1.0 - cobertura)) / alfa + 0.5)
        px[i + 3] = int(alfa * 255.0 + 0.5)

    def rect_relleno(self, x0, y0, x1, y1, rgb):
        for y in range(max(0, int(math.floor(y0))), min(self.alto, int(math.ceil(y1)))):
            for x in range(max(0, int(math.floor(x0))), min(self.ancho, int(math.ceil(x1)))):
                self.mezclar(x, y, rgb, 1.0)

    def linea(self, x1, y1, x2, y2, grosor, rgb):
        """Segmento con antialias, grosor en pixeles."""
        radio = grosor / 2.0
        xi = int(math.floor(min(x1, x2) - radio - 1))
        xf = int(math.ceil(max(x1, x2) + radio + 1))
        yi = int(math.floor(min(y1, y2) - radio - 1))
        yf = int(math.ceil(max(y1, y2) + radio + 1))
        xi, yi = max(0, xi), max(0, yi)
        xf, yf = min(self.ancho - 1, xf), min(self.alto - 1, yf)
        for y in range(yi, yf + 1):
            for x in range(xi, xf + 1):
                d = _dist_segmento(x + 0.5, y + 0.5, x1, y1, x2, y2)
                self.mezclar(x, y, rgb, _cobertura(d, radio))

    def rect_contorno(self, x0, y0, x1, y1, grosor, rgb):
        self.linea(x0, y0, x1, y0, grosor, rgb)
        self.linea(x0, y1, x1, y1, grosor, rgb)
        self.linea(x0, y0, x0, y1, grosor, rgb)
        self.linea(x1, y0, x1, y1, grosor, rgb)

    def circulo(self, cx, cy, radio, grosor, rgb, filtro=None):
        """Aro de espesor `grosor`; `filtro(x, y)` permite dibujar solo un arco."""
        borde = grosor / 2.0
        xi = max(0, int(math.floor(cx - radio - borde - 1)))
        xf = min(self.ancho - 1, int(math.ceil(cx + radio + borde + 1)))
        yi = max(0, int(math.floor(cy - radio - borde - 1)))
        yf = min(self.alto - 1, int(math.ceil(cy + radio + borde + 1)))
        for y in range(yi, yf + 1):
            for x in range(xi, xf + 1):
                if filtro is not None and not filtro(x + 0.5, y + 0.5):
                    continue
                d = abs(math.hypot(x + 0.5 - cx, y + 0.5 - cy) - radio)
                self.mezclar(x, y, rgb, _cobertura(d, borde))

    def disco(self, cx, cy, radio, rgb, filtro=None):
        xi = max(0, int(math.floor(cx - radio - 1)))
        xf = min(self.ancho - 1, int(math.ceil(cx + radio + 1)))
        yi = max(0, int(math.floor(cy - radio - 1)))
        yf = min(self.alto - 1, int(math.ceil(cy + radio + 1)))
        for y in range(yi, yf + 1):
            for x in range(xi, xf + 1):
                if filtro is not None and not filtro(x + 0.5, y + 0.5):
                    continue
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                self.mezclar(x, y, rgb, _cobertura(d, radio))

    def poligono(self, puntos, rgb):
        """Relleno por escaneo (point-in-polygon) dentro del bounding box."""
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]
        xi = max(0, int(math.floor(min(xs))))
        xf = min(self.ancho - 1, int(math.ceil(max(xs))))
        yi = max(0, int(math.floor(min(ys))))
        yf = min(self.alto - 1, int(math.ceil(max(ys))))
        n = len(puntos)
        for y in range(yi, yf + 1):
            py = y + 0.5
            for x in range(xi, xf + 1):
                if _dentro(puntos, n, x + 0.5, py):
                    self.mezclar(x, y, rgb, 1.0)

    def reducir(self, factor):
        """Promedio de bloques factor x factor (antialias por supersampling)."""
        ancho = self.ancho // factor
        alto = self.alto // factor
        salida = bytearray(ancho * alto * 4)
        src = self.px
        for y in range(alto):
            for x in range(ancho):
                r = g = b = a = 0
                for dy in range(factor):
                    base = ((y * factor + dy) * self.ancho + x * factor) * 4
                    for dx in range(factor):
                        i = base + dx * 4
                        alfa = src[i + 3]
                        r += src[i] * alfa
                        g += src[i + 1] * alfa
                        b += src[i + 2] * alfa
                        a += alfa
                n = factor * factor
                j = (y * ancho + x) * 4
                if a:
                    salida[j] = r // a
                    salida[j + 1] = g // a
                    salida[j + 2] = b // a
                salida[j + 3] = a // n
        resultado = Lienzo(ancho, alto)
        resultado.px = salida
        return resultado

# --------------------------------------------------------------------------
# Cancha de futbol (vertical)
# --------------------------------------------------------------------------
def generar_campo(ruta, ancho=720, alto=1280):
    verde_claro = (77, 175, 80)
    verde_oscuro = (62, 152, 66)
    blanco = (255, 255, 255)

    lienzo = Lienzo(ancho, alto, verde_claro + (255,))

    # Franjas horizontales
    franjas = 14
    alto_franja = alto / float(franjas)
    for i in range(franjas):
        if i % 2 == 1:
            lienzo.rect_relleno(0, i * alto_franja, ancho, (i + 1) * alto_franja, verde_oscuro)

    # Medidas reales de una cancha (68 m x 105 m) escaladas a la imagen
    margen = 40
    x0, y0 = margen, margen
    x1, y1 = ancho - margen, alto - margen
    esc = (x1 - x0) / 68.0              # pixeles por metro
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    lw = max(3.0, 0.16 * esc)           # grosor de linea

    # Limites y linea de medio campo
    lienzo.rect_contorno(x0, y0, x1, y1, lw, blanco)
    lienzo.linea(x0, cy, x1, cy, lw, blanco)

    # Circulo y punto central
    lienzo.circulo(cx, cy, 9.15 * esc, lw, blanco)
    lienzo.disco(cx, cy, 0.35 * esc, blanco)

    # Areas (grande y chica) + punto penal + semicirculo, arriba y abajo
    area_ancho = 40.32 * esc
    area_prof = 16.5 * esc
    chica_ancho = 18.32 * esc
    chica_prof = 5.5 * esc
    punto = 11.0 * esc
    radio_arco = 9.15 * esc

    for arriba in (True, False):
        base = y0 if arriba else y1
        signo = 1.0 if arriba else -1.0
        lienzo.rect_contorno(cx - area_ancho / 2.0, base,
                             cx + area_ancho / 2.0, base + signo * area_prof, lw, blanco)
        lienzo.rect_contorno(cx - chica_ancho / 2.0, base,
                             cx + chica_ancho / 2.0, base + signo * chica_prof, lw, blanco)
        py = base + signo * punto
        lienzo.disco(cx, py, 0.35 * esc, blanco)
        limite = base + signo * area_prof
        if arriba:
            lienzo.circulo(cx, py, radio_arco, lw, blanco,
                           filtro=lambda x, y, lim=limite: y > lim)
        else:
            lienzo.circulo(cx, py, radio_arco, lw, blanco,
                           filtro=lambda x, y, lim=limite: y < lim)

    # Arcos de esquina (un cuarto de circulo dentro de la cancha)
    esquinas = ((x0, y0, 1.0, 1.0), (x1, y0, -1.0, 1.0),
                (x0, y1, 1.0, -1.0), (x1, y1, -1.0, -1.0))
    for ex, ey, sx, sy in esquinas:
        lienzo.circulo(ex, ey, 1.0 * esc, lw, blanco,
                       filtro=lambda x, y, ex0=ex, ey0=ey, sx0=sx, sy0=sy:
                       (x - ex0) * sx0 >= 0 and (y - ey0) * sy0 >= 0)

    # Porterias (red) dibujadas fuera de la linea de meta
    porteria = 7.32 * esc
    fondo = 2.2 * esc
    for base, signo in ((y0, -1.0), (y1, 1.0)):
        lienzo.rect_contorno(cx - porteria / 2.0, base,
                             cx + porteria / 2.0, base + signo * fondo, lw, blanco)
        for k in range(1, 6):
            xv = cx - porteria / 2.0 + porteria * k / 6.0
            lienzo.linea(xv, base, xv, base + signo * fondo, lw * 0.5, blanco)

    escribir_png(ruta, ancho, alto, lienzo.px)

# --------------------------------------------------------------------------
# Balon
# --------------------------------------------------------------------------
def _pentagono(cx, cy, radio, angulo_inicial):
    puntos = []
    for k in range(5):
        a = math.radians(angulo_inicial + 72 * k)
        puntos.append((cx + radio * math.cos(a), cy + radio * math.sin(a)))
    return puntos


def generar_balon(ruta, tam=512):
    ss = 3                      # supersampling para bordes suaves
    n = tam * ss
    blanco = (252, 252, 252)
    negro = (18, 18, 18)

    lienzo = Lienzo(n, n, (0, 0, 0, 0))
    cx = cy = n / 2.0
    radio = n * 0.47

    lienzo.disco(cx, cy, radio, blanco)

    radio_penta = radio * 0.31
    lienzo.poligono(_pentagono(cx, cy, radio_penta, -90), negro)

    for k in range(5):
        ang = math.radians(-90 + 72 * k)
        px = cx + math.cos(ang) * radio * 0.72
        py = cy + math.sin(ang) * radio * 0.72
        lienzo.poligono(_pentagono(px, py, radio_penta, -90 + 72 * k), negro)

    lienzo.circulo(cx, cy, radio * 0.96, radio * 0.08, negro)

    # Recorta todo lo que quede fuera del circulo del balon
    for y in range(n):
        for x in range(n):
            if math.hypot(x + 0.5 - cx, y + 0.5 - cy) > radio:
                lienzo.px[(y * n + x) * 4 + 3] = 0

    reducir = lienzo.reducir(ss)
    escribir_png(ruta, tam, tam, reducir.px)


def main():
    if not os.path.isdir(DIR_ASSETS):
        os.makedirs(DIR_ASSETS)
    print("Generando imagenes del proyecto...")
    generar_campo(os.path.join(DIR_ASSETS, "campo.png"))
    generar_balon(os.path.join(DIR_ASSETS, "balon.png"))
    print("Listo.")


if __name__ == "__main__":
    main()
