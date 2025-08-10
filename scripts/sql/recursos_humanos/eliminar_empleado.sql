UPDATE empleados
SET activo = 0, estado = 'INACTIVO', fecha_modificacion = GETDATE()
WHERE id = ?