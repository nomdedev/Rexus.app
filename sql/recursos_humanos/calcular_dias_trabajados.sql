-- Calcular días trabajados por empleado en un mes
SELECT COUNT(DISTINCT fecha) FROM asistencias 
WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
AND tipo != 'FALTA'
