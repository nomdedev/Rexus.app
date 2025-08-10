-- scripts/sql/logistica/contar_entregas_mes_actual.sql
-- Cuenta las entregas programadas para el mes actual
SELECT COUNT(*) FROM [entregas]
WHERE MONTH(fecha_programada) = MONTH(GETDATE())
AND YEAR(fecha_programada) = YEAR(GETDATE())