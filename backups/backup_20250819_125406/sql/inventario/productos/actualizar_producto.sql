UPDATE [inventario]
SET
    descripcion = @descripcion,
    categoria = @categoria,
    unidad_medida = @unidad_medida,
    precio_compra = @precio_compra,
    precio_venta = @precio_venta,
    stock_minimo = @stock_minimo,
    ubicacion = @ubicacion,
    observaciones = @observaciones,
    usuario_modificador = @usuario_modificador,
    fecha_modificacion = GETDATE()
WHERE id = @producto_id AND activo = 1;