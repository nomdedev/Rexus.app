SELECT
    COUNT(*) as total_completadas,
    DATEDIFF(day, ?, ?) as dias_periodo,
    CASE
        WHEN DATEDIFF(day, ?, ?) > 0
        THEN CAST(COUNT(*) AS FLOAT) / DATEDIFF(day, ?, ?)
        ELSE 0.0
    END as promedio_diario
FROM obras
WHERE estado = 'COMPLETADA'
  AND fecha_finalizacion BETWEEN ? AND ?