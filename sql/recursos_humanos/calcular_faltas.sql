-- Calcular faltas de un empleado en un mes
SELECT COUNT(*) FROM asistencias 
WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
AND tipo = 'FALTA'
