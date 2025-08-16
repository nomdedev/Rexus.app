## Auditoría: rexus/modules/auditoria/controller.py

Resumen
- Archivo: `rexus/modules/auditoria/controller.py`
- Alcance: Filtrado, exportación y limpieza de registros de auditoría; registro de acciones.

Hallazgos clave
- Funcionalidad completa para exportar a CSV/Excel (usa pandas/openpyxl) y limpieza con confirmación.
- Buen uso de `registrar_accion` para anotar operaciones importantes.
- Uso intensivo de `self.view` para mensajes y confirmaciones.

Riesgos y severidad
- Dependencias: medio — exportar a Excel requiere pandas y openpyxl; manejar ImportError ya hecho.
- Seguridad: bajo — confirmaciones antes de limpieza crítica.

Recomendaciones
1. Añadir límites y paginación a exportaciones para evitar OOM con grandes volúmenes.
2. Añadir pruebas para `_exportar_excel` y manejo de ImportError.
3. Añadir logging de exportaciones (quién, cuándo, cuántos registros).

Estado: informe creado.
