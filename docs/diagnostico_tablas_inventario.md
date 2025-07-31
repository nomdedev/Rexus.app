# Diagnóstico de Tablas de la Base de Datos `inventario`

Fecha de análisis: 30/07/2025

---

## Tablas que el sistema utiliza activamente

- **inventario_perfiles**: Catálogo principal de productos/materiales. Usada en todos los módulos de inventario, pedidos, reservas, reportes, movimientos, etc.
- **historial**: Registro de movimientos de inventario (entradas, salidas, ajustes). Usada para auditoría y reportes.
- **reserva_materiales** / **reservas_inventario**: Gestión de reservas de materiales para obras.
- **lotes_inventario**: Seguimiento de lotes, vencimientos y series.
- **movimientos_inventario**: Reportes avanzados de movimientos (algunos módulos).
- **materiales_obra**: Asignación de materiales a obras.
- **obras**: Referencia cruzada para asignaciones y reportes.

---

## Tablas que existen pero NO se usan (o están obsoletas/sin sentido)

- **inventario**: Hay queries que la buscan, pero la lógica real usa `inventario_perfiles`. Puede estar obsoleta.
- **pedidos_material**: El sistema busca esta tabla, pero la tabla real usada es `pedidos_compra`.
- **pedidos_herrajes**: El sistema busca esta tabla, pero la tabla real es `herrajes_por_obra`.
- **pagos_pedidos**: El sistema busca esta tabla, pero la tabla real es `pago_por_obra`.
- **vidrios**: La tabla real usada es `vidrios_por_obra`.
- **otros nombres antiguos**: `materiales`, `movimientos_stock`, `reservas_stock`, etc. (pueden estar en la BD pero no se usan en el código actual).

---

## Recomendaciones

- **Eliminar o migrar** las tablas obsoletas que no se usan en el código actual.
- **Actualizar queries** en los modelos para que usen los nombres correctos de tablas.
- **Mantener solo las tablas activas** para evitar confusión y errores futuros.

---

> Si tienes dudas sobre alguna tabla específica, revisa los scripts en `tools/development/database/analisis_tablas.py` y `analizar_tablas_faltantes.py` para ver el mapeo completo y los propósitos de cada tabla.

---

**GitHub Copilot - Diagnóstico automático**
