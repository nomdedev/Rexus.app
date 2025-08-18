-- Query completa de estadísticas de obras con todas las métricas
-- Optimizada para obtener todas las estadísticas en una sola consulta

SELECT
    COUNT(*) as total_obras,
    SUM(CASE WHEN estado = 'EN_PROCESO' THEN 1 ELSE 0 END) as obras_activas,
    SUM(CASE WHEN estado = 'FINALIZADA' THEN 1 ELSE 0 END) as obras_finalizadas,
    SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as obras_pendientes,
    AVG(CASE WHEN presupuesto_total > 0 THEN presupuesto_total ELSE NULL END) as presupuesto_promedio,
    SUM(CASE WHEN presupuesto_total > 0 THEN presupuesto_total ELSE 0 END) as presupuesto_total_acumulado
FROM obras
WHERE activo = 1