# notebooks/

| Notebook | Qué responde |
|---|---|
| `analisis.ipynb` | Qué aporta cada modo de la madre y si el rescate reduce la varianza del tiempo de convergencia (hipótesis de `referencia/resumen.pdf`). Lee `../experimentos/datos/`; deja las figuras en `figuras/`. |

Abrirlo con Jupyter o VS Code usando el Python del entorno `aco-gemelo`. Para volver a ejecutarlo completo
sin abrirlo (desde esta carpeta):

```
python -X utf8 -m jupyter nbconvert --to notebook --execute --inplace analisis.ipynb
```

Las conclusiones del final se calculan a partir de los datos: si se vuelven a correr los experimentos, cambian solas.
