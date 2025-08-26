-- Calcular horas extra por empleado en un mes
SELECT SUM(horas_extra) FROM asistencias 
WHERE empleado_id = ? AND MONTH(fecha) = ? AND YEAR(fecha) = ?
