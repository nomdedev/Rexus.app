SELECT ISNULL(MAX(CAST(SUBSTRING(numero_recibo, 4, 10) AS INT)), 0) + 1
FROM recibos
WHERE numero_recibo LIKE 'REC-%'
