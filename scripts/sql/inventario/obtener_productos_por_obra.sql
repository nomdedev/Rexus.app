-- Obtiene productos asignados a una obra específica
SELECT i.id, i.codigo, i.descripcion, i.categoria, i.stock_actual,
       mo.cantidad as cantidad_asignada, mo.estado, mo.fecha_asignacion,
       mo.etapa_id, mo.observaciones
FROM materiales_obra mo
INNER JOIN inventario_perfiles i ON mo.producto_id = i.id
WHERE mo.obra_id = ?
ORDER BY mo.fecha_asignacion DESC