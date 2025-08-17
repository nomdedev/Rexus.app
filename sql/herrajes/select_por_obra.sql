-- Consulta segura para obtener herrajes asignados a una obra
-- Utiliza la tabla consolidada 'productos_obra'
-- Los parámetros se deben pasar usando prepared statements

SELECT 
    po.id, po.obra_id, po.producto_id, po.cantidad_requerida, 
    po.cantidad_asignada, po.cantidad_utilizada, po.etapa_obra,
    po.fecha_asignacion, po.observaciones,
    p.codigo, p.descripcion, p.categoria, p.subcategoria, p.tipo,
    p.unidad_medida, p.precio_unitario, p.stock_actual
FROM productos_obra po
INNER JOIN productos p ON po.producto_id = p.id
WHERE po.obra_id = ? AND p.categoria = 'HERRAJE' AND po.activo = 1
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND po.etapa_obra = ?
    -- AND p.subcategoria = ?
ORDER BY po.fecha_asignacion;