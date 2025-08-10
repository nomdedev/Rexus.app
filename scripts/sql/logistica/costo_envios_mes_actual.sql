-- scripts/sql/logistica/costo_envios_mes_actual.sql
-- Suma el costo total de envíos del mes actual
SELECT SUM(costo_envio) FROM [entregas]
WHERE MONTH(fecha_programada) = MONTH(GETDATE())
AND YEAR(fecha_programada) = YEAR(GETDATE())