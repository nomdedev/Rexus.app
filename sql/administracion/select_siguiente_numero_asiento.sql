-- Obtener siguiente número de asiento contable
SELECT ISNULL(MAX(CAST(SUBSTRING(numero_asiento, 4, 10) AS INT)), 0) + 1 AS siguiente_numero
FROM [{tabla_libro_contable}]
