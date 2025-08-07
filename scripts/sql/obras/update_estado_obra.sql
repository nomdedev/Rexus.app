UPDATE obras
SET estado = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
WHERE id = ?