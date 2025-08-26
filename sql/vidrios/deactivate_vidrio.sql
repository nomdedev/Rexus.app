-- Desactivar vidrio (soft delete)
UPDATE vidrios SET activo = 0, fecha_actualizacion = GETDATE()
WHERE id = ?;
