SELECT tipo_recibo, SUM(monto)
FROM recibos
WHERE
    (? IS NULL OR fecha_emision >= ?)
    AND (? IS NULL OR fecha_emision <= ?)
GROUP BY tipo_recibo