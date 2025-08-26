-- Obtiene todo el historial de mantenimientos
SELECT mp.id, mp.equipo_id, e.nombre, mp.tipo, mp.fecha_programada, 
       mp.fecha_ejecucion, mp.estado, mp.observaciones
FROM mantenimientos_programados mp
JOIN equipos e ON mp.equipo_id = e.id
ORDER BY mp.fecha_programada DESC
