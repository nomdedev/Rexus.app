-- Obtener obras activas con paginación (SQLite)
SELECT 
    id,
    COALESCE(nombre_obra, descripcion, 'Sin nombre') as nombre,
    descripcion,
    estado,
    fecha_inicio,
    COALESCE(fecha_fin_estimada, fecha_fin_real) as fecha_fin,
    direccion as ubicacion,
    fecha_creacion,
    fecha_fin_real,
    COALESCE(presupuesto_total, 0) as presupuesto_total,
    COALESCE(progreso, 0) as progreso,
    COALESCE(etapa_actual, 'No definida') as etapa_actual
FROM obras
WHERE activo = 1
ORDER BY fecha_creacion DESC
LIMIT ? OFFSET ?