-- Obtiene recibos con filtros opcionales
-- Parámetros: fecha_desde, fecha_hasta, tipo (pueden ser NULL)
SELECT 
    id, numero_recibo, fecha_emision, tipo_recibo, concepto,
    beneficiario, monto, moneda, estado, impreso,
    usuario_creacion, fecha_creacion
FROM recibos
WHERE 
    (? IS NULL OR fecha_emision >= ?)
    AND (? IS NULL OR fecha_emision <= ?)
    AND (? IS NULL OR ? = 'Todos' OR tipo_recibo = ?)
ORDER BY fecha_emision DESC, numero_recibo DESC