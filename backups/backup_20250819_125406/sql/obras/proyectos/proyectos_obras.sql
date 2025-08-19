SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.fecha_fin_real,
    o.presupuesto,
    o.costo_real,
    o.direccion,
    o.notas,
    o.created_at,
    o.updated_at
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE o.id = ?;
SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto,
    o.direccion
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
ORDER BY o.fecha_inicio DESC;
INSERT INTO obras (
    nombre,
    descripcion,
    cliente_id,
    estado,
    fecha_inicio,
    fecha_fin_estimada,
    presupuesto,
    direccion,
    notas,
    created_at,
    updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE());
UPDATE obras
SET
    nombre = ?,
    descripcion = ?,
    cliente_id = ?,
    estado = ?,
    fecha_inicio = ?,
    fecha_fin_estimada = ?,
    fecha_fin_real = ?,
    presupuesto = ?,
    costo_real = ?,
    direccion = ?,
    notas = ?,
    updated_at = GETDATE()
WHERE id = ?;
UPDATE obras
SET
    estado = ?,
    updated_at = GETDATE()
WHERE id = ?;
UPDATE obras
SET
    fecha_fin_real = ?,
    estado = 'completada',
    updated_at = GETDATE()
WHERE id = ?;
UPDATE obras
SET
    deleted_at = GETDATE(),
    updated_at = GETDATE()
WHERE id = ?;
DELETE FROM obras WHERE id = ?;
SELECT DISTINCT estado
FROM obras
WHERE estado IS NOT NULL
ORDER BY estado;
SELECT
    o.id,
    o.nombre,
    COUNT(t.id) AS total_tareas,
    COUNT(CASE WHEN t.estado = 'completada' THEN 1 END) AS tareas_completadas,
    CASE
        WHEN COUNT(t.id) > 0 THEN
            (COUNT(CASE WHEN t.estado = 'completada' THEN 1 END) * 100.0 / COUNT(t.id))
        ELSE 0
    END AS porcentaje_progreso
FROM obras o
LEFT JOIN tareas_obra t ON o.id = t.obra_id
WHERE o.id = ?
GROUP BY o.id, o.nombre;
SELECT id, nombre, activo
FROM clientes
WHERE id = ? AND activo = 1;
SELECT id, nombre, fecha_inicio, fecha_fin_estimada
FROM obras
WHERE cliente_id = ?
  AND estado IN ('activa', 'en_progreso', 'planificada')
  AND (
    (fecha_inicio BETWEEN ? AND ?) OR
    (fecha_fin_estimada BETWEEN ? AND ?) OR
    (fecha_inicio <= ? AND fecha_fin_estimada >= ?)
  );
SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE o.estado = ?
ORDER BY o.fecha_inicio DESC;
SELECT
    id,
    nombre,
    estado,
    created_at
FROM obras
ORDER BY created_at DESC;