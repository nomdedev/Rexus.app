UPDATE inventario_perfiles
SET tipo = ?, ancho_mm = ?, alto_mm = ?, largo_mm = ?,
    peso_kg = ?, color = ?, descripcion = ?, precio_unitario = ?,
    stock_actual = ?, stock_minimo = ?, proveedor = ?,
    fecha_modificacion = GETDATE()
WHERE id = ?