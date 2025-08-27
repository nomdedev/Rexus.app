-- Obtener suma total de compras (sin columna descuento)
SELECT 
    ISNULL(SUM(total), 0) as monto_total
FROM compras 
WHERE estado != 'CANCELADO'