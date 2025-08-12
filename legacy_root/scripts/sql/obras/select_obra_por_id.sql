SELECT
    id, codigo, nombre, cliente, estado, responsable,
    fecha_inicio, fecha_fin_estimada, presupuesto_total,
    tipo_obra, progreso, descripcion, ubicacion,
    created_at, updated_at
FROM obras
WHERE id = ?