-- Consulta segura para obtener movimientos de inventario
-- Utiliza la tabla consolidada 'movimientos_inventario'
-- Los parámetros se deben pasar usando prepared statements

SELECT 
    id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
    tipo_movimiento, cantidad, unidad_medida, stock_anterior, stock_nuevo,
    precio_unitario, documento_referencia, obra_id, motivo, observaciones,
    usuario_movimiento, fecha_movimiento
FROM movimientos_inventario
WHERE activo = 1 AND estado = 'CONFIRMADO'
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND producto_id = ?
    -- AND tipo_movimiento = ?
    -- AND fecha_movimiento >= ?
ORDER BY fecha_movimiento DESC;