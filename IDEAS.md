# IDEAS — cuaderno de asociación libre del operador

Este cuaderno es del **operador**. Aquí entra cualquier idea, intuición o imagen tal como salga: sin justificar,
sin orden y sin pedir permiso. Es el lugar de la "función impulso": una entrada breve que puede mover todo el sistema.

## Reglas

1. **Nadie corrige ni juzga lo que se escribe aquí.** Claude y los agentes no editan el texto de una idea, no la
   resumen y no la "mejoran".
2. **Las ideas no tienen que ser verificables para entrar.** La verificación viene después, en otro lugar
   (`DECISIONES-PRUEBA.md`, `FAILURES.md`, experimentos), y solo si el operador quiere.
3. Una idea que se vuelve hipótesis o decisión **se queda aquí intacta**. Lo único que se agrega, debajo y aparte,
   es una línea **"→ Qué pasó"** con el enlace a donde se trabajó.
4. Siguiendo PROMPT-ZERO, las intuiciones sin verificar son **"malicia indígena"**: hipótesis que se respetan y se
   prueban; nunca requisitos y nunca descartadas por falta de rigor.
5. Para agregar una idea basta con escribirla abajo, con la fecha, o decírsela a Claude para que la anote **tal cual**.

---

## Ideas

Las primeras entradas son intuiciones que el operador ya había dicho en la conversación; se anotan con sus palabras.

### 2026-11-16 — Hormigas y abejas
> "Inspírate en las hormigas y las abejas. ¿Cómo tratarías de pasar esto al clon de software a construir? Ten en
> cuenta que tienen una especie de oráculo madre que ve todo pero su memoria es limitada. Usa lo que puedas de
> inteligencia de enjambre."

→ Qué pasó: la madre como pista de baile y rescate, y su memoria en bytes (`DECISIONES-PRUEBA.md`, F1–F3;
`gemelo/aco_gemelo/madre/`).

### 2026-11-16 — Llegar, avisar y verificar
> "Mensaje a la madre para decir que llegó, la madre actualiza a las demás… cuando la última llegue se logró conocer
> el camino. Luego se manda una última agente que salga desde el origen a la meta y que confirme si llegó con las otras."

→ Qué pasó: la agente verificadora y el criterio de convergencia (`DECISIONES-PRUEBA.md`, D3 y G1).

### 2026-11-16 — Mensajes claros y feromónicos
> "Que haya claridad en mensajes Madre–Agentes y agentes–agentes (cortos / feromónicos)."

→ Qué pasó: `PROTOCOLO.md` (familias de mensajes y su tamaño en bits).

### 2026-11-17 — Obstáculos aleatorios
> "El mundo puede tener los obstáculos aleatorios, lo importante es que haya un camino entre el inicio y el fin."

→ Qué pasó: el escenario aleatorio en los experimentos (`gemelo/configs/aleatorio.yaml`).

### 2026-11-18 — Mirar lo que hizo otro
> "Haz un análisis de este y revela hallazgos, resalta cosas que de pronto no tuviste en cuenta."

→ Qué pasó: el análisis del trabajo de Gemini, que destapó el defecto del rescate
(`otras/ANALISIS-gemini-artefacto9.md`; `FAILURES.md` F-020).

### 2026-11-18 — Ver lo que sabe la madre
> "Alguna gráfica donde se tenga el conocimiento global del mundo en fotogramas, a medida que la madre va recibiendo
> datos de los agentes."

→ Qué pasó: plan D3 y registro tick a tick del mapa de la madre (`PLAN-MEJORAS.md`, C3 y D3).

### 2026-11-18 — Un divulgador
> "Un nuevo agente llamado documentador o divulgador… ojalá estilo divulgadores de lujo como Carl Sagan o Edward Wilson."

→ Qué pasó: `.claude/agents/divulgador.md` y `gemelo/docs/divulgacion/`.

### 2026-11-18 — Asociación libre
> "Lo que no quiero perder es lo que los psicoanalistas llaman la asociación libre… ¿esto generaría riesgo de que se
> pierda la intuición, que es como una función impulso?"

→ Qué pasó: este cuaderno.

---

*(Escribe aquí las siguientes.)*
