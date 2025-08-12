-- 🔒 Estadísticas de reservas por obra y categoría
-- Reemplaza f-string vulnerable por consulta parametrizada
SELECT
    i.categoria,
    COUNT(*) as cantidad_items,
    SUM(r.cantidad_reservada) as cantidad_total,
    SUM(r.cantidad_reservada * i.precio_unitario) as valor_total
FROM reserva_materiales r
INNER JOIN inventario_perfiles i ON r.producto_id = i.id
WHERE r.obra_id = @obra_id 
    AND r.estado = 'ACTIVA'
GROUP BY i.categoria
ORDER BY valor_total DESC;
