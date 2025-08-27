-- estadisticas_movimientos_ultimo_mes.sql
-- Obtiene estadísticas de movimientos del último mes
-- Sin parámetros

SELECT
    tipo_movimiento,
    COUNT(*) as total_movimientos,
    SUM(ABS(cantidad)) as cantidad_total,
    AVG(ABS(cantidad)) as cantidad_promedio
FROM movimientos_inventario
WHERE fecha_movimiento >= DATEADD(MONTH, -1, GETDATE())
GROUP BY tipo_movimiento