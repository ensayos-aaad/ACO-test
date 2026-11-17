# CHECKLIST — software necesario

Verificado en la máquina local el 2026-11-16 a las 19:46 -0500, por comandos. No se instaló ni se
cambió nada.
- `[x]` instalado y verificado.
- `[ ]` falta, o falta configurarlo o probarlo.

**Intérprete oficial del proyecto:** el Python de Anaconda, `C:\Users\Usuario\anaconda3\python.exe`
(Anaconda3 2024.10-1, Python 3.12.7, conda 25.1.1, entorno `base`).

## 1. Python (Anaconda) — oráculo y notebooks

- [x] Anaconda3 2024.10-1 · Python 3.12.7 · conda 25.1.1
- [x] numpy 1.26.4
- [x] scipy 1.13.1 (pruebas estadísticas para C1–C3)
- [x] matplotlib 3.9.2
- [x] sympy 1.13.1 (deneubourg [9] y [15])
- [x] pandas 2.2.3
- [x] statsmodels 0.14.2 (intervalos de confianza para proporciones)
- [x] pytest 7.4.4 (pruebas del oráculo)
- [x] nbconvert 7.16.4 (ejecutar notebooks sin interfaz)
- [x] IPython 8.27.0 · notebook 7.2.2 · jupyterlab 4.2.5
- [x] pyserial 3.5 (leer la salida serial del ESP32)
- [ ] **ipywidgets 7.8.1 es incompatible con Notebook 7 / JupyterLab 4**: los sliders de
      `experimento_doble_puente` y `montecarlo_aco` pueden no aparecer (widgetsnbextension 3.6.6 y
      jupyterlab_widgets 1.0.0 son de la generación anterior). Hace falta ipywidgets 8 o abrirlos en
      VS Code. El oráculo no depende de esto, porque correrá sin widgets.
- [ ] **El `python` del PATH no es Anaconda**: `where python` devuelve primero `C:\Python311\python.exe`.
      Hay que llamar a Anaconda por su ruta completa, usar el *Anaconda Prompt* o corregir el PATH.
      (Hay además Python 3.8.8 y 2.7.15 instalados.)
- [ ] Decidir si se usa el entorno `base` o un entorno conda propio del proyecto, con
      `environment.yml` para fijar las versiones (C5, reproducibilidad).

## 2. NetLogo — entorno simulado

- [x] NetLogo 7.0.4 (`C:\Program Files\NetLogo 7.0.4`)
- [x] Extensión `py` incluida en NetLogo (los modelos de referencia usan
      `py:setup "C:/Users/Usuario/anaconda3/python.exe"`)
- [x] Extensión `arduino` incluida en NetLogo (alternativa a `py` + pyserial)
- [x] Java 8u511 y JDK 16.0.1 (NetLogo trae su propio Java; se registra por si acaso)
- [ ] Probar la cadena NetLogo `py:setup` → Anaconda → `import serial` en esta máquina
      (no se ha ejecutado).

## 3. ESP32 — firmware

- [x] VS Code 1.146.0
- [x] PlatformIO IDE (extensión) + PlatformIO Core 6.1.19
- [x] Plataforma `espressif32` 6.3.1 en PlatformIO (`board = nodemcu-32s` de la referencia)
- [x] Arduino IDE 2.3.2 (más Arduino 1.8.15) con el core ESP32 3.0.5 (alternativa a PlatformIO)
- [x] Drivers USB-serial: CP210x (`silabser.inf`, `slabvcp.inf`) y CH340 (`ch341ser.inf`)
- [x] Extensión Serial Monitor de VS Code
- [ ] Elegir la toolchain (PROMPT-ZERO §3: Arduino IDE, PlatformIO o ESP-IDF). La referencia usa PlatformIO.
- [ ] Librería de LEDs direccionables (FastLED o Adafruit NeoPixel), solo si el artefacto los usa (§3).
- [ ] ESP-NOW (viene con el core ESP32), solo si se usan varios nodos (§3).

## 4. Simulación del firmware (Wokwi)

- [ ] **Extensión Wokwi para VS Code** (`wokwi.wokwi-vscode`): no está instalada. Necesita una
      licencia gratuita que se renueva periódicamente.
- [ ] O bien usar Wokwi en el navegador (wokwi.com, sin instalar nada; la referencia lo usó en
      `ejemplo3`). Decidir cuál de las dos.

## 5. Comunicación serial NetLogo ↔ ESP32

- [x] Puertos serial virtuales: HHD Free Virtual Serial Ports, con el par COM1 ↔ COM2 activo
      (los usaron los ejemplos 4 y 5 de la referencia)
- [ ] Probar el par virtual COM1 ↔ COM2 con pyserial desde Anaconda.

## 6. Control de versiones

- [x] Git 2.32.0 (el remoto `origin` funciona; ya se hizo un push)
- [x] GitHub Desktop 2.9.6 · GitKraken 12.6.2
- [ ] GitHub CLI (`gh`): no está instalado. Es opcional; solo hace falta para manejar PRs o issues
      desde la terminal.

## 7. Documentación

- [x] Claude Code dentro de VS Code
- [ ] Linter de Markdown: VS Code marca avisos de formato (MD022, MD032, MD060) en los `.md` del
      proyecto. Son cosméticos; decidir si se corrigen o se desactivan esas reglas.
