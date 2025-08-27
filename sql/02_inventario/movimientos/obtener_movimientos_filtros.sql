-- obtener_movimientos_filtros.sql
-- Obtiene movimientos con filtros base (sin WHERE dinámicos)
-- Los filtros se agregan dinámicamente en el código Python
-- Sin parámetros base

SELECT
    m.id, m.producto_id, m.tipo_movimiento, m.cantidad,
    m.stock_anterior, m.stock_nuevo, m.observaciones,
    m.obra_id, m.usuario, m.fecha_movimiento,
    p.codigo, p.descripcion
FROM movimientos_inventario m
INNER JOIN inventario p ON m.producto_id = p.id
WHERE 1=1