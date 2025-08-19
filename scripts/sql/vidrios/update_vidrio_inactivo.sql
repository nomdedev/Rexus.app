UPDATE [vidrios]
SET estado = 'INACTIVO', fecha_actualizacion = GETDATE()
WHERE id = ?;