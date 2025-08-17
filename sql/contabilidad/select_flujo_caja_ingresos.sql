-- Obtiene ingresos por tipo de recibo para el flujo de caja
-- Parámetros: fecha_desde, fecha_hasta (pueden ser NULL)
SELECT tipo_recibo, SUM(monto)
FROM recibos 
WHERE 
    (? IS NULL OR fecha_emision >= ?)
    AND (? IS NULL OR fecha_emision <= ?)
GROUP BY tipo_recibo