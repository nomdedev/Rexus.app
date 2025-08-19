SELECT categoria, SUM(monto)
FROM pagos_obra
WHERE
    (? IS NULL OR fecha_pago >= ?)
    AND (? IS NULL OR fecha_pago <= ?)
GROUP BY categoria