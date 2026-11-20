# Revisión del bloque D (D1–D8)

**Autor:** agente `revisor` · **Fecha:** 2026-11-20 (≈ 03:40–03:51 -0500) · **Revisado:** árbol de trabajo sobre `6f4319a` ·
Scripts de recálculo en `revision_D/` (`verif1.py`, `verif_modos.py`, `verif_canal.py`).

**Veredicto: NO PASA**, solo por textos (F-028). Lo técnico pasa.

| Punto | Veredicto | Evidencia |
|---|---|---|
| Ejecución desde cero (comando del README) | PASA | Copia con `figuras/` vacía: 31 s, 9 PNG embebidas, salidas de texto idénticas |
| D7: figuras desde el repositorio | PASA | Las 10 figuras regeneradas (y el GIF) con el mismo md5, también tras `test_notebook.py` |
| Reglas de selección | PASA | Semilla 2026, fijada en `default.yaml` desde `b7d3fb9`; cuadros 0, 6, 12, 18, 23, 29, 35, 41 (tope 41). Solo están declaradas en el notebook, sin marca de hora fuera |
| D2 y D3: mecanismos | PASA | La ruta verificada no repite celdas; en el tick 41 los obstáculos de la madre son exactamente los reales; nunca hay obstáculos falsos; el conocimiento llega al 100 % (tick 41) antes de que las 6 agentes lleguen a la meta (tick 75) |
| D4 y D5 | PASA | Tamaños = `tamanos()`; no caben en ESP-NOW PERCEPCION (490 B) y MAPA (396 B); familia 0 entre 90 y 100 %; familia 1 = 0 |
| Conclusiones (sección 7) | PASA | Iguales a `6f4319a` salvo los rótulos "Figura N" |
| Suites | PASA | 318 del gemelo y 7 del oráculo (en la copia) |
| D6: "Qué mirar" | NO PASA | Hallazgos 1–3 |
| D8: cifras | NO PASA (parcial) | Casi todo coincide con los CSV; excepciones 4 y 5 |
| D8: confirmatorio frente a exploratorio | PASA con salvedad | Hallazgo 6 |

## Hallazgos

1. "Qué mirar" de la figura 1: "las dos rutas miden el doble de la óptima o más"; la razón sin madre es 1,88.
2. "Qué mirar" de la figura 2: "con solo 6 agentes el primer camino reforzado tiende a ganar" es un mecanismo no medido (F-017
   lo deja abierto). Con madre, las celdas con más feromona no están en la ruta verificada.
3. Sección 1: "difusión es el único modo que guarda un mapa" (rescate también, `madre.py:104`); "tres ensayos en vivo" (son dos).
4. `experimento_modos.md`: familia 0 "entre el 94 y el 100 %"; en difusión es el 92,0 % (mínimo por ensayo, 90,0 %). Rangos
   "5 000-5 700 mensajes" (mínimo 4 775) y "4,3 a 6,3 KB" (mínimo 4 240 B).
5. `experimento_rescate.md`: "llega tarde" explicado como "ya tenía ruta"; el contador es `rescate_ya_llego` (ya llegó a la
   meta) y `rescate_ya_tiene_ruta` = 0. Citaba "(a) y (d) de abajo", que están en `rescate_tras_F020.md`.
6. Horas estimadas en los informes de D8 (03:35–03:50), posteriores a la escritura de los archivos (03:31).
7. Leves: la regla dice "valor final" y el código usaba `max` (aquí da igual); la feromona de la figura 2 se normaliza por panel
   sin decirlo; `docs/divulgacion/01_la_colonia_y_la_madre.md` incrusta f1–f4, que ahora se titulan "Figura 4/5/6/9";
   `test_notebook.py` regenera figuras que están en git (con otra versión de matplotlib cambiarían).

**No comprobado:** que las reglas de selección se fijaran antes de ver los resultados (no hay registro con hora fuera del
notebook); F-027(1) no se reprodujo (solo se vio que `jupyter-nbconvert` de Anaconda base está en el PATH); no se repitieron
experimentos.

## Segunda pasada (≈ 03:57–04:27 -0500)

Hallazgos 1 a 6 **corregidos** (PASA cada uno; notebook desde cero con salidas, conclusiones y md5 de figuras idénticos;
318 + 7 pruebas en PASA). Veredicto **NO PASA** por una afirmación más, que ya estaba en la primera versión:

- **N1 (moderado):** `experimento_modos.md` y `experimento_rescate.md` decían que el rescate con umbral 0,5 "solo cuesta
  el tráfico de `ESTADO`"; en rescate las agentes también envían `FRAGMENTO` y `DANZA` (semilla 0, L: ESTADO 223, FRAGMENTO
  57, DANZA 61; ESTADO es el 60 % de los bytes hacia la madre).
- **N2 (leve):** "la feromona premia el camino que más se usó" omite que el depósito por defecto pesa por la calidad de la
  ruta (255 ÷ largo, `agente.py:469`).
- **N3 (muy leve):** "usados 70-83 %"; lo medido va del 71,1 al 83,2 %.
- Leves abiertos: las figuras f1–f4 incrustadas en `docs/divulgacion/01_...` llevan ahora "Figura 4/5/6/9"; `test_notebook.py`
  regenera figuras versionadas en git.

N1–N3 corregidos por el orquestador tras esta pasada (ver F-028); pendiente de confirmar.

## Tercera pasada, corta (≈ 04:35 -0500)

N1 y N3 **PASA**; notebook guardado con 9 imágenes y salidas que coinciden con los datos. **NO PASA** por la frase nueva de N2,
escrita por el orquestador: "cada viaje deposita más feromona cuanto más corta es su ruta" es falso por viaje (el depósito
por celda es 255 ÷ largo y se aplica a las `largo` celdas: el total por viaje es casi constante, 0,94–1,02 τ) y "el rastro
es la suma de todos los viajes" omite la evaporación (1 % por tick; en el ensayo de la figura el máximo llega a 0,706 y
termina en 0,283). Observación muy leve: la lista de N1 omitía `PIDE_RESCATE` (< 0,1 % de los bytes).
**Corrección aplicada con la redacción que propuso el revisor, sin cambios**, y `PIDE_RESCATE` agregado a la lista.
