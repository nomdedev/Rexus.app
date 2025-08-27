UPDATE [vidrios]
SET codigo = ?, descripcion = ?, tipo = ?, espesor = ?, proveedor = ?,
    precio_m2 = ?, color = ?, tratamiento = ?, dimensiones_disponibles = ?,
    estado = ?, observaciones = ?, fecha_actualizacion = GETDATE()
WHERE id = ?;