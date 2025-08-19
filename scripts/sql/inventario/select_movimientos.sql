SELECT
    id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
    tipo_movimiento, cantidad, unidad_medida, stock_anterior, stock_nuevo,
    precio_unitario, documento_referencia, obra_id, motivo, observaciones,
    usuario_movimiento, fecha_movimiento
FROM movimientos_inventario
WHERE activo = 1 AND estado = 'CONFIRMADO'
ORDER BY fecha_movimiento DESC;