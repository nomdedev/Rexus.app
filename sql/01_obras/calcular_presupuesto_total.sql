-- Script para calcular el presupuesto total de una obra (SQLite)
-- Parámetros: :obra_id
-- Retorna: Presupuesto total calculado

SELECT 
    o.id as obra_id,
    COALESCE(o.nombre_obra, o.descripcion, 'Sin nombre') as obra_nombre,
    COALESCE(o.presupuesto_total, 0) as presupuesto_base,
    COALESCE(o.costo_actual, 0) as costo_actual,
    COALESCE(o.margen_estimado, 0) as margen_estimado,
    COALESCE(materiales.total_materiales, 0) as costo_materiales,
    COALESCE(mano_obra.total_mano_obra, 0) as costo_mano_obra,
    COALESCE(otros.total_otros, 0) as otros_gastos,
    (
        COALESCE(o.presupuesto_total, 0) + 
        COALESCE(materiales.total_materiales, 0) + 
        COALESCE(mano_obra.total_mano_obra, 0) + 
        COALESCE(otros.total_otros, 0)
    ) as presupuesto_total_calculado,
    CASE 
        WHEN COALESCE(o.costo_actual, 0) > 0 THEN 
            ((COALESCE(o.costo_actual, 0) - (
                COALESCE(materiales.total_materiales, 0) + 
                COALESCE(mano_obra.total_mano_obra, 0) + 
                COALESCE(otros.total_otros, 0)
            )) / COALESCE(o.costo_actual, 1)) * 100
        ELSE 0
    END as margen_real_porcentaje
FROM obras o
LEFT JOIN (
    -- Calcular total de materiales si existe tabla de materiales_obra
    SELECT 
        obra_id,
        SUM(cantidad * precio_unitario) as total_materiales
    FROM detalles_obra 
    WHERE tipo_detalle = 'Material'
        AND activo = 1
    GROUP BY obra_id
) materiales ON o.id = materiales.obra_id
LEFT JOIN (
    -- Calcular total de mano de obra
    SELECT 
        obra_id,
        SUM(cantidad * precio_unitario) as total_mano_obra
    FROM detalles_obra 
    WHERE tipo_detalle = 'Mano de Obra'
        AND activo = 1
    GROUP BY obra_id
) mano_obra ON o.id = mano_obra.obra_id
LEFT JOIN (
    -- Calcular otros gastos
    SELECT 
        obra_id,
        SUM(cantidad * precio_unitario) as total_otros
    FROM detalles_obra 
    WHERE tipo_detalle NOT IN ('Material', 'Mano de Obra')
        AND activo = 1
    GROUP BY obra_id
) otros ON o.id = otros.obra_id
WHERE o.id = :obra_id
  AND o.activo = 1;