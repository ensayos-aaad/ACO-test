# oraculo/

Aquí se ejecuta la implementación de referencia (los notebooks de `../referencia/`) para producir
los valores contra los que se valida el firmware.

Reglas:
- No se edita nada en `../referencia/`. El código se importa o se copia aquí, **citando el archivo
  y la celda de origen** en un comentario.
- Las pruebas estocásticas fijan y registran la semilla del RNG (C5).
- La prueba estadística, el número de ensayos y la tolerancia se declaran **antes** de correr
  cada prueba, y el operador los aprueba.

Estado: vacía. Todavía no hay código; falta que el operador apruebe los criterios C1–C6.
Candidatos y vacíos detectados: ver `../CONTEXT.md` §3 y §4.
