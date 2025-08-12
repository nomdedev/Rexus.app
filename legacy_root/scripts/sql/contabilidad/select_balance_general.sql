-- Obtiene el balance general para un período
-- Parámetros: fecha_desde, fecha_hasta (pueden ser NULL)
SELECT 
    tipo_asiento,
    SUM(debe) as total_debe,
    SUM(haber) as total_haber,
    SUM(saldo) as saldo_neto
FROM libro_contable
WHERE 
    estado = 'ACTIVO'
    AND (? IS NULL OR fecha_asiento >= ?)
    AND (? IS NULL OR fecha_asiento <= ?)
GROUP BY tipo_asiento