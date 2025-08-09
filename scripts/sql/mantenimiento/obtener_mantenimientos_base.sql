-- Obtener mantenimientos con filtros
SELECT 
    m.id, m.equipo_id, m.tipo_mantenimiento, m.fecha_programada,
    m.fecha_realizada, m.tecnico_responsable, m.estado,
    m.tiempo_estimado, m.tiempo_real, m.costo_estimado, m.costo_real,
    m.observaciones, m.repuestos_utilizados, m.herramientas_utilizadas,
    e.nombre as equipo_nombre, e.codigo as equipo_codigo,
    e.ubicacion as equipo_ubicacion
FROM mantenimientos m
INNER JOIN equipos e ON m.equipo_id = e.id
WHERE m.activo = 1
ORDER BY m.fecha_programada DESC;
