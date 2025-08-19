SELECT 
    id,
    nombre,
    descripcion,
    estado,
    fecha_inicio,
    fecha_fin_estimada as fecha_fin,
    direccion as ubicacion,
    fecha_creacion,
    fecha_fin_real,
    presupuesto_total,
    progreso,
    etapa_actual
FROM obras
WHERE activo = 1
ORDER BY fecha_creacion DESC
OFFSET ? ROWS
FETCH NEXT ? ROWS ONLY