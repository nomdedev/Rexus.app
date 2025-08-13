-- Consulta optimizada para obtener obras paginadas
-- Incluye cálculos de progreso y estado mejorado
-- Parámetros: offset, limit

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
    -- Campos calculados
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
        WHEN fecha_fin_estimada IS NOT NULL
        THEN julianday(fecha_fin_estimada) - julianday('now')
        ELSE NULL
    END as dias_restantes
FROM obras
WHERE activo = 1
ORDER BY 
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