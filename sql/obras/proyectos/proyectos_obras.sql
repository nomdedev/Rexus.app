-- Consultas SQL para gestión de proyectos de obras
-- Archivo: proyectos_obras.sql

-- Consulta para obtener obra por ID
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
WHERE o.id = %s;

-- Consulta para obtener todas las obras con información básica
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

-- Consulta para insertar nueva obra
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
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());

-- Consulta para actualizar obra
UPDATE obras 
SET 
    nombre = %s,
    descripcion = %s,
    cliente_id = %s,
    estado = %s,
    fecha_inicio = %s,
    fecha_fin_estimada = %s,
    fecha_fin_real = %s,
    presupuesto = %s,
    costo_real = %s,
    direccion = %s,
    notas = %s,
    updated_at = NOW()
WHERE id = %s;

-- Consulta para cambiar estado de obra
UPDATE obras 
SET 
    estado = %s,
    updated_at = NOW()
WHERE id = %s;

-- Consulta para actualizar fecha fin real (cuando se completa)
UPDATE obras 
SET 
    fecha_fin_real = %s,
    estado = 'completada',
    updated_at = NOW()
WHERE id = %s;

-- Consulta para eliminar obra (soft delete si existe campo deleted_at)
UPDATE obras 
SET 
    deleted_at = NOW(),
    updated_at = NOW()
WHERE id = %s;

-- Consulta alternativa para eliminar obra (hard delete)
DELETE FROM obras WHERE id = %s;

-- Consulta para obtener estados disponibles
SELECT DISTINCT estado 
FROM obras 
WHERE estado IS NOT NULL 
ORDER BY estado;

-- Consulta para calcular progreso de obra basado en tareas completadas
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
WHERE o.id = %s
GROUP BY o.id, o.nombre;

-- Consulta para validar cliente antes de asignar obra
SELECT id, nombre, activo 
FROM clientes 
WHERE id = %s AND activo = TRUE;

-- Consulta para verificar conflictos de fechas
SELECT id, nombre, fecha_inicio, fecha_fin_estimada
FROM obras 
WHERE cliente_id = %s 
  AND estado IN ('activa', 'en_progreso', 'planificada')
  AND (
    (fecha_inicio BETWEEN %s AND %s) OR
    (fecha_fin_estimada BETWEEN %s AND %s) OR
    (fecha_inicio <= %s AND fecha_fin_estimada >= %s)
  );

-- Consulta para obtener obras por estado
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
WHERE o.estado = %s
ORDER BY o.fecha_inicio DESC;

-- Consulta para obtener última obra creada
SELECT 
    id,
    nombre,
    estado,
    created_at
FROM obras 
ORDER BY created_at DESC 
LIMIT 1;
