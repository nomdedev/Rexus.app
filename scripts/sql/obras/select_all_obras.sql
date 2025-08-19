SELECT
    id, codigo, nombre, descripcion, cliente,
    fecha_inicio, fecha_fin_estimada, fecha_fin_real,
    etapa_actual, estado, progreso,
    presupuesto_total, costo_actual, margen_estimado,
    ubicacion, responsable, observaciones,
    activo, created_at, updated_at
FROM obras
WHERE activo = 1
ORDER BY fecha_inicio DESC;