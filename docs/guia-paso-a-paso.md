# Guía paso a paso — PenalBot

Tutorial para rehacer el proyecto desde cero en MIT App Inventor 2, con los
mismos nombres de componentes que usa el archivo `appinventor/PenalBot.aia`.

## 0. Antes de empezar

* Cuenta de Google y navegador actualizado.
* App **MIT AI2 Companion** instalada en el teléfono (Play Store) o un emulador.
* Las dos imágenes del proyecto: `assets/campo.png` y `assets/balon.png`.

## 1. Crear el proyecto

1. Entrar a <https://ai2.appinventor.mit.edu>.
2. **Proyectos → Empezar nuevo proyecto**, nombre `PenalBot`.
3. En **Paleta → Media** (o en *Assets*), subir `campo.png` y `balon.png`.

## 2. Diseñador: componentes

Arrastrar los componentes en este orden (el orden define el lugar en pantalla):

| # | Desde la paleta | Renombrar a | Propiedades |
|---|---|---|---|
| 1 | *User Interface → Label* | `LblTitulo` | `Text` = `Arrastra el balón para patearlo`; `Width` = *Fill parent*; `BackgroundColor` = `#14532D`; `TextColor` = blanco; `FontSize` = 16; `FontBold` = ✓; `TextAlignment` = *center* |
| 2 | *Drawing and Animation → Canvas* | `Lienzo1` | `Width` = *Fill parent*; `Height` = *Fill parent*; `BackgroundImage` = `campo.png` |
| 3 | *Drawing and Animation → ImageSprite* (dentro del lienzo) | `Bola` | `Picture` = `balon.png`; `Width` = `44`; `Height` = `44`; `X` = `150`; `Y` = `280`; `Speed` = `0`; `Heading` = `0` |
| 4 | *Layout → HorizontalArrangement* | `FilaInferior` | `Width` = *Fill parent*; `AlignHorizontal` = *center*; `AlignVertical` = *center* |
| 5 | *User Interface → Button* (dentro de la fila) | `BtnReiniciar` | `Text` = `Reiniciar balón`; `BackgroundColor` = `#14532D`; `TextColor` = blanco; `Shape` = *rounded* |
| 6 | *User Interface → Label* (dentro de la fila) | `LblRebotes` | `Text` = `Rebotes: 0`; `TextColor` = blanco; `FontSize` = 16 |

También en `Screen1`: `Title` = `Penales LOBOS BUAP`, `AlignHorizontal` =
*center*, `Sizing` = *Responsive*, `BackgroundColor` = `#0B2E0B`.

> Al arrastrar `ImageSprite`, App Inventor lo coloca **dentro** del `Lienzo1`.
> Lo mismo con el botón y la etiqueta: deben quedar dentro de `FilaInferior`.

## 3. Bloques

Abrir la pestaña **Bloques**.

### 3.1 Variable global

* `Variables → inicializar global` → renombrar la variable a `rebotes` y dejar
  el valor `0`.

### 3.2 Al iniciar la pantalla

* `Screen1 → cuando Screen1 .Inicializar`.
* `Bola → poner Bola .Velocidad como` → `0`.
* `LblRebotes → poner LblRebotes .Texto como` → bloque de texto `"Rebotes: 0"`
  (`Texto → ""`).

### 3.3 Cuando se lanza el balón

1. `Bola → cuando Bola .Lanzado` (evento *Flung*). El bloque trae los parámetros
   `x`, `y`, `velocidad`, `dirección`, `velx`, `vely`.
2. `Bola → poner Bola .Dirección como` y conectar el parámetro `dirección`
   (bloque naranja que sale del evento).
3. `Bola → poner Bola .Velocidad como` → número `50`.
4. `Bola → llamar Bola .MoverA` → conectar `x` en el primer casillero e `y` en el
   segundo.

Queda igual que la captura de la consigna:

```
cuando Bola .Lanzado  x  y  velocidad  dirección  velx  vely
hacer   poner Bola .Dirección  →  [dirección]
        poner Bola .Velocidad  →  50
        llamar Bola .MoverA  x:[x]  y:[y]
```

### 3.4 Cuando el balón toca un borde

1. `Bola → cuando Bola .BordeAlcanzado` (evento *EdgeReached*), con el parámetro
   `borde`.
2. `Bola → llamar Bola .Rebotar` y conectar `borde`.
3. `Control → si / entonces / si no`:
   * condición: `Matemáticas → 0 > 0` cambiado a `>` con
     `Bola .Velocidad` a la izquierda y `10` a la derecha;
   * entonces: `poner Bola .Velocidad como ( Bola .Velocidad - 10 )`
     (`Matemáticas → 0 - 0`);
   * si no: `poner Bola .Velocidad como 0`.
4. `Variables → poner global` `rebotes` como
   `Matemáticas → 0 + 0` con `global rebotes` y `1`.
5. `LblRebotes → poner LblRebotes .Texto como` → `Texto → unir` con el texto
   `"Rebotes: "` y `global rebotes`.

```
cuando Bola .BordeAlcanzado  borde
hacer   llamar Bola .Rebotar  [borde]
        si Bola .Velocidad > 10 entonces poner Bola .Velocidad como (Bola .Velocidad - 10)
        si no poner Bola .Velocidad como 0
        poner global rebotes como (global rebotes + 1)
        poner LblRebotes .Texto como unir "Rebotes: " (global rebotes)
```

### 3.5 Botón reiniciar

```
cuando BtnReiniciar .Clic
hacer   poner global rebotes como 0
        poner LblRebotes .Texto como "Rebotes: 0"
        poner Bola .Velocidad como 0
        llamar Bola .MoverA
               x: ( Lienzo1 .Ancho / 2 )
               y: ( Lienzo1 .Alto / 2 )
```

`Lienzo1 .Ancho` y `Lienzo1 .Alto` están en `Lienzo1 → get Ancho` y
`get Alto`; la división es `Matemáticas → 0 / 0`.

## 4. Probar en el teléfono

1. **Conectar → AI Companion** y escanear el código QR.
2. Probar el fling: el balón debe salir en la dirección del gesto.
3. Probar los rebotes: cada choque contra un borde resta 10 de velocidad y suma
   un rebote al contador; a los 5 rebotes el balón queda quieto.
4. Probar el botón: el balón vuelve al centro y el contador a 0.

## 5. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| El balón no se mueve al lanzarlo | `Velocidad` quedó en 0 o el sprite tiene `Enabled` desmarcado | Poner `Velocidad` = 50 en el evento `Lanzado` y marcar `Enabled` |
| El balón atraviesa el borde sin rebotar | Falta el bloque `Rebotar` o no se le pasó `borde` | Conectar el parámetro `borde` en `Rebotar` |
| Se mueve para atrás y nunca se detiene | La velocidad se volvió negativa | Usar el `si ... entonces ... si no` de la sección 3.4 |
| El fondo no cubre la pantalla | `Lienzo1` tiene tamaño fijo | `Width` y `Height` = *Fill parent* |
| El balón aparece fuera de la cancha | `X`/`Y` iniciales muy grandes | `X` = 150, `Y` = 280 en el diseñador |
| Al girar el teléfono se desacomoda | `Sizing` fijo | `Screen1.Sizing` = *Responsive* |

## 6. Empaquetar el proyecto

* **Proyectos → Exportar proyecto seleccionado (.aia)** genera el archivo para
  entregar.
* Para el APK: **Compilar → Android App (.apk)**.

En este repositorio el `.aia` se reconstruye con:

```bash
python3 herramientas/construir_aia.py
```
