SELECT
    id,
    codigo_obra,
    nombre_obra,
    cliente,
    descripcion,
    direccion,
    telefono_contacto,
    fecha_inicio,
    fecha_fin_estimada,
    presupuesto_total,
    presupuesto_utilizado,
    estado,
    tipo_obra,
    prioridad,
    responsable,
    observaciones,
    fecha_creacion,
    fecha_actualizacion,
    CASE
        WHEN presupuesto_total > 0
        THEN ROUND((presupuesto_utilizado * 100.0 / presupuesto_total), 2)
        ELSE 0.0
    END as porcentaje_presupuesto_usado,
    CASE
        WHEN fecha_fin_estimada < DATE('now') AND estado NOT IN ('FINALIZADA', 'CANCELADA')
        THEN 'VENCIDA'
        WHEN fecha_fin_estimada <= DATE('now', '+7 days') AND estado NOT IN ('FINALIZADA', 'CANCELADA')
        THEN 'PROXIMA_VENCER'
        ELSE 'EN_TIEMPO'
    END as estado_temporal,
    CASE
        WHEN codigo_obra LIKE ? THEN 1
        WHEN nombre_obra LIKE ? THEN 2
        WHEN cliente LIKE ? THEN 3
        WHEN direccion LIKE ? THEN 4
        WHEN descripcion LIKE ? THEN 5
        ELSE 6
    END as relevancia_busqueda
FROM obras
WHERE activo = 1
  AND (
    codigo_obra LIKE ? OR
    nombre_obra LIKE ? OR
    cliente LIKE ? OR
    direccion LIKE ? OR
    descripcion LIKE ? OR
    responsable LIKE ?
  )
ORDER BY
    relevancia_busqueda ASC,
    CASE prioridad
        WHEN 'ALTA' THEN 1
        WHEN 'MEDIA' THEN 2
        WHEN 'BAJA' THEN 3
        ELSE 4
    END,
    CASE estado
        WHEN 'EN_PROCESO' THEN 1
        WHEN 'PLANIFICACION' THEN 2
        WHEN 'PAUSADA' THEN 3
        WHEN 'FINALIZADA' THEN 4
        WHEN 'CANCELADA' THEN 5
        ELSE 6
    END,
    fecha_creacion DESC
LIMIT ? OFFSET ?;