-- Consulta para buscar obras que usan exactamente un código específico de inventario
-- Utilizado en obras_asociadas_dialog.py para mostrar obras asociadas a un producto de inventario

SELECT DISTINCT
    o.id as obra_id,
    o.nombre as obra_nombre,
    d.detalle,
    d.cantidad,
    d.precio_unitario,
    d.precio_total,
    ISNULL(o.estado, 'Activa') as estado
FROM obras o
INNER JOIN detalles_obra d ON o.id = d.obra_id
WHERE d.codigo_inventario = @codigo_inventario
ORDER BY o.nombre, d.detalle
