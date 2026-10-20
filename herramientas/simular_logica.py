#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simula en Python la logica de los bloques del proyecto PenalBot para
comprobar que el comportamiento es el esperado:

  * al lanzar el balon se fija la direccion y la velocidad (50),
  * en cada borde el balon rebota y pierde 10 de velocidad,
  * cuando la velocidad llega a 10 o menos, el balon se detiene,
  * el contador de rebotes aumenta y el boton "Reiniciar" lo devuelve a cero.

No es el codigo de App Inventor: es un modelo de los mismos bloques que
permite verificar la logica sin un telefono Android.

Uso:  python3 herramientas/simular_logica.py
"""

import math

ANCHO = 360          # ancho tipico del lienzo en dp
ALTO = 600           # alto tipico del lienzo en dp
TAM_BALON = 44       # propiedad Width/Height del sprite
INTERVALO_MS = 100   # intervalo por omision del sprite


class Bola(object):
    def __init__(self):
        self.x = 150.0
        self.y = 280.0
        self.heading = 0.0
        self.speed = 0.0
        self.rebotes = 0
        self.eventos = []

    # --- bloques ---------------------------------------------------------
    def lanzado(self, x, y, heading):
        """cuando Bola.Lanzado -> fija direccion, velocidad 50 y se mueve al toque."""
        self.heading = heading
        self.speed = 50
        self.mover_a(x, y)
        self.eventos.append(("lanzado", round(self.speed, 1), round(self.heading, 1)))

    def mover_a(self, x, y):
        """Bola.MoverA: el origen del sprite queda dentro del lienzo."""
        self.x = min(max(float(x), 0.0), ANCHO - TAM_BALON)
        self.y = min(max(float(y), 0.0), ALTO - TAM_BALON)

    def rebotar(self, borde):
        """Bola.Rebotar(borde): refleja la direccion (igual que App Inventor)."""
        angulo = self.heading % 360
        if borde == "Este" and (angulo < 90 or angulo > 270):
            self.heading = 180 - angulo
        elif borde == "Oeste" and 90 < angulo < 270:
            self.heading = 180 - angulo
        elif borde == "Norte" and 0 < angulo < 180:
            self.heading = 360 - angulo
        elif borde == "Sur" and angulo > 180:
            self.heading = 360 - angulo

    def borde_alcanzado(self, borde):
        """cuando Bola.BordeAlcanzado: rebota, baja la velocidad y cuenta."""
        self.rebotar(borde)
        if self.speed > 10:
            self.speed -= 10
        else:
            self.speed = 0
        self.rebotes += 1
        self.eventos.append(("borde", borde, round(self.speed, 1), self.rebotes))

    def reiniciar(self):
        """cuando BtnReiniciar.Click."""
        self.rebotes = 0
        self.speed = 0
        self.mover_a(ANCHO / 2.0, ALTO / 2.0)

    # --- reloj interno del sprite ---------------------------------------
    def paso(self):
        if self.speed <= 0:
            return False
        rad = math.radians(self.heading)
        nuevo_x = self.x + self.speed * math.cos(rad)
        nuevo_y = self.y - self.speed * math.sin(rad)
        borde = None
        if nuevo_x <= 0:
            nuevo_x, borde = 0.0, "Oeste"
        elif nuevo_x >= ANCHO - TAM_BALON:
            nuevo_x, borde = ANCHO - TAM_BALON, "Este"
        if nuevo_y <= 0:
            nuevo_y, borde = 0.0, "Norte"
        elif nuevo_y >= ALTO - TAM_BALON:
            nuevo_y, borde = ALTO - TAM_BALON, "Sur"
        self.x, self.y = nuevo_x, nuevo_y
        if borde:
            self.borde_alcanzado(borde)
        return True


def simular(segundos=8):
    bola = Bola()
    bola.lanzado(180, 300, 45)          # gesto diagonal hacia arriba-derecha

    pasos_maximos = int(segundos * 1000 / INTERVALO_MS)
    pasos = 0
    while bola.speed > 0 and pasos < pasos_maximos:
        if not bola.paso():
            break
        pasos += 1
        assert 0 <= bola.x <= ANCHO - TAM_BALON, "el balon salio del lienzo (x)"
        assert 0 <= bola.y <= ALTO - TAM_BALON, "el balon salio del lienzo (y)"

    return bola, pasos


def main():
    bola, pasos = simular()

    print("Simulacion del proyecto PenalBot")
    print("Lienzo: %dx%d dp, balon: %d dp, intervalo: %d ms" % (
        ANCHO, ALTO, TAM_BALON, INTERVALO_MS))
    print("Eventos:")
    for evento in bola.eventos:
        print("  ", evento)
    print("Velocidad final: %s" % bola.speed)
    print("Rebotes: %d en %.1f s" % (bola.rebotes, pasos * INTERVALO_MS / 1000.0))

    # Verificaciones de la logica de los bloques
    assert bola.rebotes == 5, "se esperaban 5 rebotes, hubo %d" % bola.rebotes
    assert bola.speed == 0, "el balon deberia quedar detenido"
    assert 0 <= bola.x <= ANCHO - TAM_BALON and 0 <= bola.y <= ALTO - TAM_BALON

    bola.reiniciar()
    assert bola.rebotes == 0 and bola.speed == 0
    assert bola.x == ANCHO / 2.0 and bola.y == ALTO / 2.0

    print("\nOK: el balon rebota, pierde velocidad, se detiene y se reinicia al centro.")


if __name__ == "__main__":
    main()
