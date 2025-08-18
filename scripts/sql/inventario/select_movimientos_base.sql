SELECT m.id, m.inventario_id, i.codigo, i.descripcion, i.categoria,
       m.tipo_movimiento, m.cantidad, m.stock_anterior, m.stock_nuevo,
       m.motivo, m.documento_referencia, m.fecha_movimiento, m.usuario,
       i.unidad_medida, i.precio_unitario
FROM movimientos_inventario m
INNER JOIN inventario_perfiles i ON m.inventario_id = i.id