-- Obtiene el equipo_id de un mantenimiento programado
SELECT equipo_id FROM mantenimientos_programados WHERE id = @programacion_id
