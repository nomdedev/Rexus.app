-- Actualizar vidrio existente
UPDATE vidrios
SET tipo = ?, especificaciones = ?, espesor = ?,
    proveedor = ?, precio_m2 = ?, color = ?,
    propiedades = ?, dimensiones = ?,
    fecha_actualizacion = GETDATE(),
    usuario_actualizacion = ?
WHERE id = ?;
