-- scripts/sql/logistica/obtener_detalle_entrega.sql
-- Obtiene el detalle de productos de una entrega específica
SELECT 
    d.id, d.entrega_id, d.producto, d.cantidad, d.peso_kg,
    d.volumen_m3, d.observaciones
FROM [detalle_entregas] d
WHERE d.entrega_id = ?
ORDER BY d.producto