UPDATE usuarios
SET nombre_completo = ?, email = ?, telefono = ?, rol = ?, estado = ?,
    fecha_modificacion = GETDATE()
WHERE id = ?