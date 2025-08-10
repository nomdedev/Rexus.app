-- Obtiene estadísticas de recibos emitidos
-- Sin parámetros
SELECT COUNT(*), SUM(monto)
FROM recibos
WHERE estado = 'EMITIDO'