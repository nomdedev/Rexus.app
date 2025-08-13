-- Actualiza un producto existente en inventario_perfiles
UPDATE inventario_perfiles
SET descripcion = ?, categoria = ?, subcategoria = ?, stock_minimo = ?,
    stock_maximo = ?, precio_unitario = ?, ubicacion = ?, proveedor = ?,
    unidad_medida = ?, observaciones = ?, fecha_modificacion = GETDATE(),
    usuario_modificacion = ?
WHERE id = ?