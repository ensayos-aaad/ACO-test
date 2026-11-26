# REPRODUCIR — guía para reproducir el gemelo desde cero

**Para quién:** cualquier persona con un computador, Git y Anaconda que quiera comprobar por su cuenta que el gemelo de
software de ACO-test da los resultados que dice el repositorio, sin preguntarle nada a nadie.
**Qué se reproduce:** la fase 1 (el gemelo en Python). Las fases 2 y 3 (NetLogo, ESP32, Raspberry Pi) todavía no tienen
nada que reproducir; sus prerrequisitos van aparte, al final de la sección 1.
**Cuánto tarda:** crear el entorno depende de la conexión; después, unos 10 minutos (pruebas ≈ 4–5 min, comparación ≈
30 s; la comparación completa, ≈ 3–4 min más). Tiempos medidos en la máquina de desarrollo (Windows 10 Pro).

> **Probado en:** la máquina de desarrollo, Windows 10 Pro con Anaconda3 2024.10-1 (conda 25.1.1) y el entorno de
> `environment.yml`. **No se ha probado en otra máquina ni en Linux o macOS** (`.handoff/rondas/002-reporte_qa.md`,
> punto 10). Si lo haces, lo que encuentres sirve: anótalo como se indica en la sección 6.

---

## 1. Prerrequisitos

### Para la fase 1 (lo que esta guía reproduce)

| Qué | Versión verificada | Para qué | Fuente |
|---|---|---|---|
| Git | cualquiera reciente | Clonar el repositorio | — |
| Anaconda o Miniconda (conda) | Anaconda3 2024.10-1, conda 25.1.1 | Crear el entorno del proyecto | `CHECKLIST-ENTORNO.md` §1 |
| Entorno `aco-gemelo` | Python 3.12.7, numpy 1.26.4, scipy 1.13.1, matplotlib 3.9.2, pandas 2.2.3, statsmodels 0.14.2, sympy 1.13.2, networkx 3.3, pyyaml 6.0.1, pillow 10.4.0, pytest 7.4.4, nbconvert 7.16.4, ipykernel 6.28.0, jupyterlab 4.2.5 | Todo el gemelo, el oráculo y el notebook | [`environment.yml`](environment.yml) |

No hace falta nada más: los notebooks de referencia que sirven de oráculo están copiados en [`../referencia/`](../referencia/).

### Para las fases 2 y 3 (todavía no se reproducen aquí)

Instalado en la máquina de desarrollo, según [`../CHECKLIST-ENTORNO.md`](../CHECKLIST-ENTORNO.md) §1–§5: NetLogo 7.0.4 (con las extensiones `py` y `arduino`), VS Code con PlatformIO Core 6.1.19 y la plataforma `espressif32` 6.3.1 (placa `nodemcu-32s`, como en la referencia), Arduino IDE 2.3.2 con el core ESP32 3.0.5, drivers USB-serie CP210x y CH340, puertos serie virtuales (par COM1 ↔ COM2) y pyserial 3.5 (en el Python de Anaconda *base*, no en `aco-gemelo`). **Sin probar todavía:** la cadena `py:setup` → Anaconda → `import serial` y el par COM1 ↔ COM2; falta instalar Wokwi y elegir la toolchain. El inventario de hardware (cuántos ESP32, la Raspberry Pi) **no está verificado** (bloqueante B4 de [`../ESTADO-PREHARDWARE.md`](../ESTADO-PREHARDWARE.md)), y la elección del transporte y del lenguaje de los agentes sigue abierta (B2 y B3).

---

## 2. Paso a paso

Los comandos están escritos para el **Anaconda Prompt** de Windows; en Linux o macOS son los mismos, con `/` en las rutas.

### 2.1 Clonar el repositorio

```
git clone https://github.com/ensayos-aaad/ACO-test.git
cd ACO-test
```

### 2.2 Crear y activar el entorno

```
conda env create -f gemelo/environment.yml
conda activate aco-gemelo
python -c "import sys; print(sys.executable, sys.version.split()[0])"
```

La última línea debe mostrar un Python **dentro de** `envs\aco-gemelo` y la versión **3.12.7**. Si muestra otro (por
ejemplo `C:\Python311\python.exe`), el PATH tiene otro Python antes que el del entorno: es la trampa de F-005 (sección 5).
Desde aquí, `python` significa ese Python del entorno.

### 2.3 Correr las pruebas

```
cd gemelo
python -B -I -X utf8 -m pytest -q -p no:cacheprovider -W ignore
cd ..
python -B -I -X utf8 -m pytest oraculo -q -p no:cacheprovider -W ignore
```

**Debe dar:** `350 passed` en el gemelo (≈ 4–5 min) y `7 passed` en el oráculo (≈ 10 s).

Una advertencia: `gemelo/tests/test_notebook.py` borra y vuelve a generar las figuras del notebook, que están en el
repositorio. Con el entorno de `environment.yml` salieron iguales en la máquina de desarrollo; `environment.yml` fija las
librerías directas, no todas sus dependencias, así que si `git status` las muestra modificadas, es una diferencia de
versiones y vale la pena anotarla.

### 2.4 Correr el escenario de referencia

El escenario de referencia es el **mundo L del plano de ensayo** con la configuración por defecto
([`configs/default.yaml`](configs/default.yaml)): semilla 2026, 6 agentes, 10 viajes cada una, la madre en modo pista de
baile.

```
cd gemelo
python -X utf8 -m aco_gemelo run --config configs/default.yaml --png resultados/final.png
```

Muestra el mundo (I = nido, F = meta, # = obstáculo) y una tabla de resultados. Las primeras líneas de la tabla deben ser:

```
semilla                      2026
escenario                    L
modo_madre                   pista_de_baile
motivo                       verificada
asentadas                    1
verificada                   1
ticks_asentadas              739
ticks_total                  760
largo_optimo                 8
largo_verificado             20
razon                        2.5
```

Es decir: las 6 agentes se asentaron en la meta en el tick 739 y la verificadora llegó siguiendo solo el rastro, por una
ruta de 20 movimientos cuando la más corta posible mide 8. La salida completa está en
[`reproducir/esperado/run_default.txt`](reproducir/esperado/run_default.txt) y la imagen en
[`reproducir/esperado/final_default.png`](reproducir/esperado/final_default.png). Que la ruta sea 2,5 veces la óptima no es
un error de la reproducción: un solo ensayo no dice cuán bueno es un modo (lo explica la sección 1 del notebook).

### 2.5 Comparar con la salida esperada

```
python -X utf8 reproducir/comparar.py
```

Corre el ensayo de 2.4 y un lote de 10 semillas en una carpeta temporal (no escribe nada en el repositorio) y lo compara
con [`reproducir/esperado/`](reproducir/esperado/). **Debe dar:**

```
Python: <ruta del entorno>\python.exe  (3.12.7)
PASA     Ensayo de referencia (texto de `run`, semilla 2026)
PASA     Lote de referencia (10 semillas, CSV)
PASA     Imagen del estado final (PNG, píxel a píxel)
Resultado: PASA. Esta máquina reproduce la salida de referencia.
```

Para comprobar también los **experimentos publicados** (480 ensayos en 18 archivos CSV, que son la base del notebook):

```
python -X utf8 reproducir/comparar.py --completo
```

Agrega dos líneas y tarda ≈ 3–4 min más (cada plan tiene 8 condiciones más su `resumen.csv`):

```
PASA     Experimento publicado `modos` (9/9 CSV iguales)
PASA     Experimento publicado `rescate` (9/9 CSV iguales)
```

### 2.6 Opcional: regenerar el notebook y la comparación con el oráculo

Los dos **reescriben archivos del repositorio**; después, `git status` y `git diff` dicen si algo cambió.

```
cd notebooks
python -X utf8 -m nbconvert --to notebook --execute --inplace analisis.ipynb
cd ../..
python -X utf8 oraculo/comparar.py
git diff --stat
```

El notebook tarda ≈ 30 s y se guarda con sus salidas; sus conclusiones (sección 7) deben ser las mismas.
`oraculo/comparar.py` tarda ≈ 13 min (corre el puente doble con muchas semillas) y reescribe
[`../oraculo/RESULTADOS.md`](../oraculo/RESULTADOS.md): C1, C2, C4 y C5 en PASA y C3 en NO PASA, con la causa documentada
en [`../oraculo/INVESTIGACION-C3.md`](../oraculo/INVESTIGACION-C3.md). `git diff` sobre ese archivo debe salir vacío.

En `git diff`, `analisis.ipynb` aparece modificado solo por las marcas de tiempo de ejecución (`iopub.*`,
`shell.execute_reply`); las salidas y las figuras de `notebooks/figuras/` no deben cambiar.

### 2.7 Si algo no coincide

1. Repite 2.2: que `python` sea el del entorno y la versión 3.12.7.
2. Repite el comando con `-X utf8`: sin él, la consola de Windows puede fallar con los acentos (F-002).
3. `comparar.py` deja lo que produjo en la carpeta temporal `aco-reproducir-ultima`: compáralo con `reproducir/esperado/`.
4. Anota lo que encontraste (sección 6).

---

## 3. Por qué cada paso

| Paso | Por qué | Dónde está el detalle |
|---|---|---|
| Entorno con versiones fijas | Los resultados dependen de las librerías (azar, gráficos); fijarlas es lo que permite exigir "igual byte a byte" | [`environment.yml`](environment.yml), artefacto 1 de [`../ARTEFACTOS.md`](../ARTEFACTOS.md) |
| Pruebas del gemelo | Cada artefacto tiene criterios de aceptación; las pruebas los comprueban (mundo, protocolo, canal, agente, madre, motores, métricas, visualización, experimentos, notebook) | [`../ARTEFACTOS.md`](../ARTEFACTOS.md), [`tests/`](tests/) |
| Pruebas del oráculo | El gemelo solo se considera correcto si reproduce los notebooks de referencia dentro de tolerancias **declaradas antes de medir** | [`../PROMPT-ZERO.md`](../PROMPT-ZERO.md) §2 y §5, [`../oraculo/TOLERANCIAS.md`](../oraculo/TOLERANCIAS.md) |
| Escenario L, semilla 2026 | Es el mundo del plano de ensayo y la configuración por defecto; con la misma semilla, el mismo resultado (criterio C5) | [`../bosquejo/`](../bosquejo/), [`configs/default.yaml`](configs/default.yaml), [`../DECISIONES-PRUEBA.md`](../DECISIONES-PRUEBA.md) |
| Comparar con la salida esperada | "Funciona" no basta: tiene que dar **lo mismo**. Las comparaciones son exactas (texto y CSV línea a línea; PNG píxel a píxel) | [`reproducir/comparar.py`](reproducir/comparar.py) |
| Experimentos publicados | Las conclusiones del notebook salen de esos 480 ensayos: si se reproducen, las conclusiones también | [`docs/informes/experimento_modos.md`](docs/informes/experimento_modos.md), [`docs/informes/experimento_rescate.md`](docs/informes/experimento_rescate.md) |
| Notebook | Explica un ensayo (mundo, feromona, mapa de la madre) y analiza los experimentos; las conclusiones se calculan de los datos | [`notebooks/analisis.ipynb`](notebooks/analisis.ipynb), [`notebooks/README.md`](notebooks/README.md) |
| Mensajes del gemelo | Agentes, madre y mundo solo se hablan por mensajes con campos y bits fijos, los mismos que usará el hardware | [`../PROTOCOLO.md`](../PROTOCOLO.md) (borrador v0.3, sin aprobar) |

La reproducibilidad se ganó con trabajo: el motor de hilos daba resultados distintos con la misma semilla cuando la red simulada perdía o retrasaba mensajes (F-023 a F-026); al endurecer la validación de las semillas se introdujo una regresión que atrapó el QA externo (F-029), y una semilla negativa repetía en silencio el mundo de la positiva (F-030). Todo está en [`../FAILURES.md`](../FAILURES.md).

---

## 4. De dónde viene: los experimentos previos de la referencia

`referencia/` es una copia de solo lectura del repositorio `UdeA-IoT/ESP-ACO` (commit `3c48648`,
[`../referencia/PROCEDENCIA.md`](../referencia/PROCEDENCIA.md)). El inventario completo está en
[`../CONTEXT.md`](../CONTEXT.md) §1. Lo que aportó cada parte:

| Material de la referencia | Qué es | Qué aportó a este proyecto |
|---|---|---|
| [`ACO/experimento_doble-puente/`](../referencia/ACO/experimento_doble-puente/) | Notebooks del puente doble de Deneubourg: la fórmula de elección (1.1), la dinámica con retardo y su estabilidad (`deneubourg_puente_doble.ipynb`), y el Montecarlo de colonias de 1000 hormigas (`montecarlo_aco.ipynb`) | **El oráculo.** `oraculo/` ejecuta el código de sus celdas tal cual y compara el gemelo con él (C1–C5). `CONTEXT.md` §3 dice qué celdas sirven y cuáles no (por ejemplo, el Montecarlo no fija semilla) |
| [`simuladores/netlogo/aspiradora/`](../referencia/simuladores/netlogo/aspiradora/) | El mundo de la aspiradora de AIMA (cap. 2) en NetLogo y Python: un agente reactivo simple y uno basado en modelo | La idea de agente que usa el gemelo: un **programa de agente** que recibe una percepción y devuelve una acción, separado del mundo (`CONTEXT.md` §6) |
| [`simulaciones/ejemplo3` a `ejemplo6`](../referencia/simulaciones/) | NetLogo como **mundo** y un agente como programa aparte, primero en Python (`ejemplo5/agente.py`) y luego en un ESP32 (`ejemplo3/esp32/`, `ejemplo6`), comunicados por serie con un protocolo síncrono de pregunta y respuesta; PlatformIO, `nodemcu-32s`, 9600 baudios; el ejemplo 4 trae el listado de puertos serie (`list-ports.py`; el 5, el mismo código en su README) y los dos, capturas de puertos virtuales | **La base de las fases 2 y 3.** El motor de hilos del gemelo sigue el mismo esquema que el ejemplo 5 (el mundo espera la acción de cada agente). Los modelos de la referencia arrancan Python desde NetLogo con `py:setup` apuntando a Anaconda (`CHECKLIST-ENTORNO.md` §2). `ejemplo6/contexto.md` deja ACO fuera de esos ejemplos a propósito |
| [`papers/1/`](../referencia/papers/1/) y [`resumen.pdf`](../referencia/resumen.pdf) | La estigmergia según Grassé y las simulaciones de Holland & Melhuish en NetLogo; `resumen.pdf` es una propuesta técnica de enjambre ESP32 + Raspberry Pi agregada por el operador (no viene del repositorio fuente, F-007) | **La estigmergia** (la feromona como mensaje que se deja en el entorno) y **la hipótesis del rescate**: que el rescate de la madre reduzca la varianza del tiempo de convergencia. El gemelo la puso a prueba y, con la configuración actual, **no quedó apoyada** (F-019, pruebas exploratorias; sección 6 del notebook) |

---

## 5. Trampas conocidas

| Trampa | Qué pasa | Cómo se evita | Registro |
|---|---|---|---|
| Consola de Windows en cp1252 | Los acentos rompen la salida (`UnicodeEncodeError`) | Siempre `python -X utf8 ...` | F-002 |
| El `python` del PATH no es el del entorno | Se corre otro intérprete y faltan librerías o cambian versiones | `conda activate aco-gemelo` y comprobar `sys.executable` (2.2) | F-005 |
| `python -m jupyter nbconvert` | Busca el subcomando en el PATH y puede ejecutar el notebook con otro Python: corre, pero sin figuras | `python -m nbconvert` (2.6) | F-027 |
| Escribir sobre los datos publicados | `aco_gemelo experimentos` escribe en `experimentos/datos/` si no se le da `--salida` | `reproducir/comparar.py --completo` usa una carpeta temporal | [`../.handoff/README.md`](../.handoff/README.md) |
| Figuras versionadas | `tests/test_notebook.py` y el paso 2.6 las regeneran | `git status` / `git diff` después (2.3, 2.6) | — |

---

## 6. Autocontenida, y cómo reportar lo que no coincida

Fuera de **clonar el repositorio** (2.1) y **descargar los paquetes de conda** (2.2), la guía no necesita internet: el
oráculo, los datos, la salida esperada y la referencia están en el repositorio.

Si algo no coincide, lo que sirve es: el paso, el comando exacto, su salida, `python -c "import sys; print(sys.version)"`
y el sistema operativo. En este proyecto, una diferencia encontrada vale más que una coincidencia supuesta: se registra en
[`../FAILURES.md`](../FAILURES.md), que nunca se borra.

**Qué no cubre esta guía:** las fases 2 y 3, la demostración con NetLogo (artefacto 16, pendiente, que tendrá su sección
aquí) y otras plataformas, que no se han probado.
