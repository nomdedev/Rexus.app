-- Script para calcular el presupuesto total de una obra
-- Parámetros: :obra_id
-- Retorna: Presupuesto total calculado

SELECT 
    o.id as obra_id,
    o.nombre as obra_nombre,
    o.presupuesto_total as presupuesto_base,
    o.costo_actual,
    o.margen_estimado,
    ISNULL(materiales.total_materiales, 0) as costo_materiales,
    ISNULL(mano_obra.total_mano_obra, 0) as costo_mano_obra,
    ISNULL(otros.total_otros, 0) as otros_gastos,
    (
        ISNULL(o.presupuesto_total, 0) + 
        ISNULL(materiales.total_materiales, 0) + 
        ISNULL(mano_obra.total_mano_obra, 0) + 
        ISNULL(otros.total_otros, 0)
    ) as presupuesto_total_calculado,
    CASE 
        WHEN o.costo_actual > 0 THEN 
            ((o.costo_actual - (
                ISNULL(materiales.total_materiales, 0) + 
                ISNULL(mano_obra.total_mano_obra, 0) + 
                ISNULL(otros.total_otros, 0)
            )) / o.costo_actual) * 100
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
    GROUP BY obra_id
) materiales ON o.id = materiales.obra_id
LEFT JOIN (
    -- Calcular total de mano de obra
    SELECT 
        obra_id,
        SUM(cantidad * precio_unitario) as total_mano_obra
    FROM detalles_obra 
    WHERE tipo_detalle = 'Mano de Obra'
    GROUP BY obra_id
) mano_obra ON o.id = mano_obra.obra_id
LEFT JOIN (
    -- Calcular otros gastos
    SELECT 
        obra_id,
        SUM(cantidad * precio_unitario) as total_otros
    FROM detalles_obra 
    WHERE tipo_detalle NOT IN ('Material', 'Mano de Obra')
    GROUP BY obra_id
) otros ON o.id = otros.obra_id
WHERE o.id = :obra_id
  AND o.activo = 1;