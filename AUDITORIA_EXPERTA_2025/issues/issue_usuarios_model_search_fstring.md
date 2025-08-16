# ISSUE: `cursor.execute` con `%{termino}%` en `usuarios/model.py`

Severidad: P1

Resumen
- En `rexus/modules/usuarios/model.py` se usa `cursor.execute(sql, (f'%{termino_busqueda.lower()}%', ...))` — revisar sanitización y límites de longitud para evitar abusos.

Acciones
- Limitar longitud y normalizar input antes de construir parámetros de búsqueda; sigue siendo parametrizado, pero validar input adicionalmente.

