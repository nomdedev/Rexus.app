-- Obtiene egresos por categoría para el flujo de caja
-- Parámetros: fecha_desde, fecha_hasta (pueden ser NULL)
SELECT categoria, SUM(monto)
FROM pagos_obra
WHERE 
    (? IS NULL OR fecha_pago >= ?)
    AND (? IS NULL OR fecha_pago <= ?)
GROUP BY categoria