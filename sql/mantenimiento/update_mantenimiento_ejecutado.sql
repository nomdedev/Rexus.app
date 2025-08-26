-- Actualiza un mantenimiento como ejecutado
UPDATE mantenimientos_programados 
SET estado = 'ejecutado', fecha_ejecucion = @fecha_ejecucion, observaciones_ejecucion = @observaciones_ejecucion
WHERE id = @programacion_id
