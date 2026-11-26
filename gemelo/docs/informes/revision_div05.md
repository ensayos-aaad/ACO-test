# Verificación de la divulgación 05, de los cambios en 03 y 04, y de ESTADO-PREHARDWARE.md

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 · **Revisado:** árbol sin commit sobre `660ee4c`.

**Veredicto:** divulgación **NO PASA** (2 medios, 4 leves); `ESTADO-PREHARDWARE.md` **NO PASA** (3 medios, 5 leves). Las cifras
están bien; fallan frases que afirman más que su fuente (F-028). Corregidas con la redacción del revisor, tal cual, sin otra
pasada (F-032).

Corrido: gemelo 350 passed; oráculo 7 passed; QA 98 recogidas (resultado no esperado; ningún texto afirma su PASA). Mecanismo
de F-031 comprobado con Pillow 10.4.0. Las dos imágenes del 05 existen.

## Divulgación

- **D1 (medio)** 05: el dato de tamaños entró al documento de bloqueantes **esta noche** (E2, historial 23:16), no "ese día".
- **D2 (medio)** 05: "la percepción en el hardware sería local, sin radio" (de `tamanos_de_mensaje.md`) no cuadra con
  `PROTOCOLO.md` (familia 0: el mundo es la autoridad) ni con `ESTADO-PREHARDWARE.md` (el mundo sigue siendo virtual). No
  está decidido cuál vale.
- **D3 (leve)** 05: de las 11 pruebas de QA, 9 atacan el comparador y 2 revisan la guía.
- **D4 (leve)** 05: "con la redacción del revisor **donde la dio**" (`revision_r003.md:52`).
- **D5 (leve)** 05: esta noche sí hubo una cifra nueva de ensayos (semilla −3: 312 frente a 430 ticks, F-030), sobre
  reproducibilidad, no sobre convergencia.
- **D6 (leve)** 03: 347 + 7 y 87 de QA son del cierre de la ronda 002 (21:02), no del cierre del día.
- Observación: `comparar.py:6` seguía con "≈ 5 min" (la guía ya decía "≈ 3–4 min").

## ESTADO-PREHARDWARE.md

- **E1 (medio)** l. 72: "la madre acelera la convergencia": claro solo con 1 viaje (F-010: 110 → 73 y 59 ticks); con 10 viajes
  la media apenas baja (465 → 433–441 en L; 428 → 390–417 en el aleatorio), sin prueba sobre la media.
- **E2 (medio)** l. 101: el patrón F-028 lo atrapó el revisor (F-028, F-030, F-031); QA no objetó la frase de F-030.
- **E3 (medio)** l. 132 (X8): que el motor de hilos libre "sigue variando" no se volvió a medir (`revision_F024.md:49`,
  `revision_F025.md:30`: no comprobado).
- **E4 (leve)** l. 20–21: F-029 no es de reproducibilidad; la reproducibilidad entre procesos la prueba
  `tests/test_reproducibilidad.py`.
- **E5 (leve)** l. 12–15: la reproducción desde cero solo se probó en la máquina de desarrollo.
- **E6 (leve)** l. 22–24 y 109: los tamaños son **calculados**, de un mensaje típico en el mundo de 8 × 8, no el máximo.
- **E7 (leve)** l. 59: la tolerancia es ±0,15 (15 puntos porcentuales), según `oraculo/TOLERANCIAS.md`.
- **E8 (leve)** l. 129: "con 32 B no le caben rutas" vale para los modos con mapa (F-011).

**Verificado sin hallazgos:** avance 15/17 y 45/49 (faltan el 16, 3 criterios, y la aprobación del protocolo, 1); 350 + 7 y 98;
tabla C1–C6; el resto del checklist; B2–B5; lo que no bloquea; X1, X2, X7; sección 6. En la divulgación: el ensayo de
referencia, lo que hace `comparar.py`, la ronda 003, F-030, los tamaños, el avance.

**No comprobado:** el resultado de las 98 pruebas de QA en esta pasada; `comparar.py --completo`, el notebook y
`oraculo/comparar.py` (cifras tomadas de la ronda 003); qué lectura de la percepción en hardware es la correcta (decisión de
diseño).
