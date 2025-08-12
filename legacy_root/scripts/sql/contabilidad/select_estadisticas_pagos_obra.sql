-- Obtiene estadísticas de pagos por obra
-- Sin parámetros
SELECT COUNT(*), SUM(monto)
FROM pagos_obra
WHERE estado = 'PAGADO'