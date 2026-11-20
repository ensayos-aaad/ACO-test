# notebooks/

| Notebook | Qué responde |
|---|---|
| `analisis.ipynb` | Cómo funciona un ensayo (una corrida comentada, feromona y trazos, el mapa de la madre), qué aporta cada modo de la madre, cuánto cuesta en la red y si el rescate reduce la varianza del tiempo de convergencia (hipótesis de `referencia/resumen.pdf`). Lee `../experimentos/datos/`; deja las figuras en `figuras/`. |

Abrirlo con Jupyter o VS Code usando el Python del entorno `aco-gemelo`. Para volver a ejecutarlo completo
sin abrirlo (desde esta carpeta, con el Python del entorno):

```
python -X utf8 -m nbconvert --to notebook --execute --inplace analisis.ipynb
```

**Ojo:** no usar `python -m jupyter nbconvert`. El lanzador `jupyter` busca el subcomando en el PATH y puede
ejecutar el notebook con otro Python (en esta máquina, el de Anaconda base); el notebook corre, pero sin las
figuras dentro (F-027).

Las conclusiones del final se calculan a partir de los datos: si se vuelven a correr los experimentos, cambian solas.

## Figuras (`figuras/`)

| Archivo | En el notebook | Qué muestra |
|---|---|---|
| `f5_un_ensayo.png` | Figura 1 | Una corrida comentada: mundo, ruta óptima y fases (semilla de `default.yaml`) |
| `f6_feromona_y_trazos.png` | Figura 2 | Feromona final, trazos de las agentes y ruta verificada, sin y con madre |
| `f7_conocimiento_de_la_madre.png` y `.gif` | Figura 3 | El mapa de la madre en el tiempo (modo difusión) |
| `f1_convergencia_por_modo.png` | Figura 4 | Convergencia por modo de la madre |
| `f2_tiempo_por_modo.png` | Figura 5 | Tiempo de convergencia por modo |
| `f3_costo_de_red.png` | Figura 6 | Beneficio frente a costo de red |
| `f8_tamano_de_mensajes.png` | Figura 7 | Tamaño de cada mensaje, binario frente a JSON, con el límite de ESP-NOW |
| `f9_trafico_por_familia.png` | Figura 8 | Tráfico por familia de mensajes y modo |
| `f4_umbral_de_rescate.png` | Figura 9 | Efecto del umbral de rescate |

Los nombres de archivo `f1` a `f4` se conservan de la primera versión (los cita `docs/divulgacion/`); el número de
figura dentro del notebook sigue el orden de lectura.
