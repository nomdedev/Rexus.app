-- Obtiene historial de mantenimientos de un equipo específico
SELECT mp.id, mp.equipo_id, e.nombre, mp.tipo, mp.fecha_programada, 
       mp.fecha_ejecucion, mp.estado, mp.observaciones
FROM mantenimientos_programados mp
JOIN equipos e ON mp.equipo_id = e.id
WHERE mp.equipo_id = @equipo_id
ORDER BY mp.fecha_programada DESC
