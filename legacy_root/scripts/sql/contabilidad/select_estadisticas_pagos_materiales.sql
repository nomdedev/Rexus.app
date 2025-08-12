-- Obtiene estadísticas de pagos de materiales
-- Sin parámetros
SELECT COUNT(*), SUM(total), SUM(pagado), SUM(pendiente)
FROM pagos_materiales