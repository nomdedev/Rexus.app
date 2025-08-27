-- Obtener siguiente número de recibo
SELECT ISNULL(MAX(CAST(SUBSTRING(numero_recibo, 4, 10) AS INT)), 0) + 1 AS siguiente_numero
FROM [{tabla_recibos}]
