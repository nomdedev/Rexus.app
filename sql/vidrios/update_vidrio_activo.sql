-- Marca un vidrio como inactivo (eliminación lógica)
UPDATE vidrios 
SET activo = 0, fecha_eliminacion = @fecha_eliminacion 
WHERE id = @vidrio_id
