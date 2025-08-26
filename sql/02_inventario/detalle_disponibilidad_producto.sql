SELECT
    stock_actual,
    stock_minimo,
    precio_unitario
FROM inventario_perfiles
WHERE id = @producto_id;