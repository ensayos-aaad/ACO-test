# Verificación de la divulgación 04 («El punto ciego») y de los cambios en 03

**Autor:** agente `revisor` · **Fecha:** 2026-11-25 · **Revisado:** `gemelo/docs/divulgacion/04_el_punto_ciego.md` (nuevo) y
`03_repetir_el_azar.md` (cambios), sin commit sobre `0234d41`.

**Veredicto: NO PASA**, por una afirmación falsa sobre un mecanismo y tres que decían más que la fuente. Corregidas con la
redacción del revisor, tal cual; sin otra pasada.

1. **(Grave)** «la semilla −3 repetía el ensayo de la 3: el mismo mundo y las mismas decisiones»: solo el **mundo**. Cada agente
   siembra con `Random(semilla*256 + id)` (`agente.py:136`): con −3, `768 − id`; con 3, `768 + id`. El canal siembra con un
   texto que incluye la semilla. Medido con el código de `ffcf646`: `default.yaml`, mismo mundo, 312 ticks con 3 y 430 con −3;
   `aleatorio.yaml`, mismo mundo, `verificadora_fallo` con 3 y `verificada` con −3. `Random(-3).getstate() == Random(3).getstate()`
   es True. El error viene de `.handoff/rondas/001-para_qa.md` (F-030).
2. **(Leve)** «ese mutante pasaba toda la suite»: según `revision_F025.md`, pasaba las 127 pruebas de canal, motor, CLI y
   experimentos; la suite entera no se corrió con el mutante.
3. **(Leve)** «se entregó a QA a las 15:19»: a esa hora quedó escrita la entrega; el turno lo pasó el operador después.
4. **(Leve)** «buscar en todo el repositorio»: el barrido de QA excluyó `referencia/`, `.handoff/` y `tests/`.

**Comprobado y correcto:** fechas y horas (ADR-004 14:03, rondas 000 14:52, 001 18:12, F-029 18:41, 002 20:51, revisión r001
15:08–15:15); recuentos de QA de las tres rondas; 21 pruebas nuevas de Desarrollo; 347 del gemelo y 87 de QA (346 sin
`test_notebook.py`); el mutante (56, 58 y 46 ticks); la prueba entre procesos; la validación de semillas; H1–H4 y quién
clasificó cada uno; O1–O3 y los −4124 s; costo y límites según `USO-DEL-PROTOCOLO.md` §6; Python 3.12.7; semillas 0–29 y
2026; los cambios en 03.

**No comprobado:** `test_notebook.py` (regenera figuras versionadas), la suite del oráculo, los 18 CSV byte a byte (se toma
de los reportes), que el comando de H1 generaba el PNG antes de la ronda (se toma de `revision_qa001.md`).
