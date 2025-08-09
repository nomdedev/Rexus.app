UPDATE obras
SET estado = ?, fecha_modificacion = CURRENT_TIMESTAMP, usuario_modificacion = ?
WHERE id = ? AND activo = 1