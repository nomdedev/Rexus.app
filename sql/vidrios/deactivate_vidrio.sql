-- Desactivar vidrio (soft delete)
UPDATE vidrios SET estado = 'INACTIVO', fecha_actualizacion = GETDATE()
WHERE id = ?;
