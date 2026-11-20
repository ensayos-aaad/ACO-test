# Revisión F-024 — nueva revisión del bloque B + C tras corregir F-023

**Autor:** agente `revisor` · **Fecha:** 2026-11-19 (≈ 22:46–23:04 -0500) · **Código revisado:** árbol de trabajo
sobre `693c694`, con las correcciones de F-024 sin commit. Scripts y mutantes en `revision_F024/` (se corren desde
`gemelo/` con `PYTHONPATH=.`; los mutantes se cargan con `-p`).

**Veredicto global: NO PASA.** Los 8 puntos de F-023 pasan; bloquea un defecto nuevo (N1) que trajo la corrección 1.

## Lo general

- 314 pruebas del gemelo y 7 del oráculo en PASA.
- Planes `modos.yaml` y `rescate.yaml` repetidos: 18 CSV idénticos byte a byte a `experimentos/datos/`.
- `referencia/` y `experimentos/datos/` sin cambios.

## Los 8 puntos de F-023: todos PASA

| # | Evidencia |
|---|---|
| 1 | `p1.py`: 0/20 distintos en cada canal, 5 corridas iguales. `r1.py`: L y aleatorio × 4 modos × 6 semillas × 4 canales (incluido JSON y p = 0,5), `hilos_sincronos` 3 veces: **0/576** distintos del determinista. El mutante "un solo generador" lo detectan 7 pruebas; el mutante "entrega en orden de llegada" solo lo detecta la prueba directa del canal, y basta |
| 2 | Tras crear la simulación solo existe el generador de la madre. Con el canal por defecto `INICIO` no cambia nada (0/30); con p = 0,2 cambia 12/30 `ticks_total` y 2/30 `motivo` (también `randint(0,0)` gasta un número). Documentado |
| 3 | `p3c.py` genera el PNG; el mutante sin el texto hace fallar 2/2 casos |
| 4 | Rechaza inicio = meta, obstáculos repetidos e inicio fuera de la cuadrícula; las claves del personalizado en otros escenarios son error; el ejemplo de `default.yaml` corre (óptima 8, verificada) |
| 5 | Cada mutante (`mut_b3`, `mut_b4`, `mut_b5`, `mut_b7`) hace fallar exactamente su prueba |
| 6 | `p6.py`: 0/30 desalineados (antes 1/30); el mutante lo detecta la prueba nueva de C3 |
| 7 | 256 y 300 dan `ValueError` claro al cargar; sin madre valen; el mutante hace fallar 4 pruebas |
| 8 | Los 8 ítems de la lista, corregidos |

Las cifras de F-024 (0/144/118 de 240; tasas sin diferencia, p de Fisher ≥ 0,08) se rehicieron con `comparar.py` y coinciden.

## Hallazgos nuevos

- **N1 (bloquea): el azar del canal de cada agente es el mismo que el de sus decisiones.** `canal.py:190` usa
  `random.Random(semilla * 256 + src)`, idéntico a `agente.py:136`, `random.Random(semilla * 256 + id_agente)`. Pérdidas y
  retardos no son independientes de las decisiones de esa agente; contradice el docstring ("su propio azar"). `r3.py`
  (semilla 3, p = 0,5, DIFUSION): 9 de los 16 números que usó el canal de la agente 1 son números que usó la agente; el
  sorteo de su primer rol y el de la pérdida de su primer mensaje son el mismo número. Con el canal por defecto no
  influye. Exploratorio (`r5.py`, aleatorio, 30 semillas, p = 0,3, retardo (0,3)): con canal independiente las
  verificadas cambian como mucho 3/30 y la mediana de ticks 2,5; sin sesgo visible, pero la independencia está rota.
- **N2 (leve):** con semilla 0, el generador del mundo (`config.py:142`, `Random(0)`) coincide con el de la madre en el
  canal; con semillas negativas, emisores distintos pueden compartir generador. El arreglo de N1 resuelve ambos.

## Lo mínimo para PASA

1. Derivar la semilla del canal con algo propio (p. ej. `random.Random(f"canal:{semilla}:{src}")`) y una prueba de que
   el generador del canal y el de la agente con el mismo id no tienen el mismo estado.
2. Repetir los dos planes publicados: deben seguir idénticos.
3. Rehacer la línea base "después" con pérdidas y retardo y actualizar las cifras de F-024.

**No comprobado:** la línea base completa (21 min); el motor `hilos` asíncrono más allá de la suite; el MP4 de un
abortado; un sesgo de N1 con suficientes semillas.
