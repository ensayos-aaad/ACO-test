# Arquitectura del motor de ejecución (Artefacto 8) y dinámica espacial de feromona

**Implementación:** `gemelo/aco_gemelo/motor/motor.py` y `gemelo/tests/test_motor.py`  
**Gráfica asociada:** `docs/img/fig3_mapa_feromona_y_trayectoria.png`

## 1. Unificación determinista y concurrente

El Artefacto 8 reemplaza el banco provisional `tests/apoyo.py` con una arquitectura de dos etapas ejecutada indistintamente por `MotorDeterminista` y `MotorHilos`:

1. **Invariante de programa de agente (decisión B1):** tanto el planificador secuencial con semilla como el grupo de hilos del sistema operativo (`_GrupoHilos`, sincronizado por tick mediante `threading.Barrier` y ordenamiento canónico de acciones por `src`) invocan exactamente el mismo método no bloqueante `Agente.paso(ahora)`. Las pruebas verifican identidad bit a bit en historial, rutas, tráfico y motivo de cierre.
2. **Ciclo de vida del ensayo en dos etapas (D3 / I4 / I5):**
   - **Etapa 1 (`exploracion`):** las $N$ exploradoras parten del nido sin conocer la meta ($\eta = 1$). Al alcanzar la meta emiten `DANZA`, eliminan bucles de su memoria de ruta ($K \le 64$) y regresan al nido depositando feromona cuantizada (`q4` en percepción, unidad $1/255$ en mundo), para luego volver a la meta y quedar en `Estado.ASENTADA`.
   - **Etapa 2 (`verificacion`):** una vez asentadas las $N$ exploradoras, el motor instancia la agente verificadora (`verificadora=True`, `informa_mapa=False`), que avanza de forma puramente explotadora guiada por el gradiente de feromona acumulado hasta confirmar la meta (`MotivoFin.VERIFICADA`) o bloquearse (`MotivoFin.VERIFICADORA_FALLO`).
3. **Cierre auditado:** ante cualquier terminación (`VERIFICADA`, `LIMITE_PASOS`, `VERIFICADORA_FALLO`, `ABORTADO`), el motor vacía mensajes pendientes dentro de la ventana de retardo (`_vaciar_pendientes`) y difunde `FIN`.

## 2. Contratos principales de `aco_gemelo.motor`

- `ConfigMotor`: agrupa `n_agentes`, `max_ticks`, `rho`, `config_agente`, `config_madre`, parámetros de canal (`radio`, `p_perdida`, `retardo`, `formato_canal`) y banderas de ejecución (`verificar`, `registrar_historial`).
- `MotorDeterminista` / `MotorHilos`: ejecutan el ensayo completo y devuelven `ResultadoEnsayo` con métricas de convergencia, tiempos por etapa, calidad frente al BFS, historial de posiciones, mapa final de feromona y desglose de tráfico por familia.
- `simular(mundo, semilla=0, config=None, multihilo=False)`: punto de entrada unificado para pruebas y lotes experimentales.
