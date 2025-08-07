-- Actualización segura de vidrio existente
-- Reemplaza f-string en actualizar_vidrio()
-- Parámetros: codigo, descripcion, tipo, espesor, proveedor, precio_m2, color, tratamiento, dimensiones_disponibles, estado, observaciones, id

UPDATE [vidrios]
SET codigo = ?, descripcion = ?, tipo = ?, espesor = ?, proveedor = ?,
    precio_m2 = ?, color = ?, tratamiento = ?, dimensiones_disponibles = ?,
    estado = ?, observaciones = ?, fecha_actualizacion = GETDATE()
WHERE id = ?;