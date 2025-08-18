SELECT l.id, l.producto_id, l.numero_lote, l.fecha_vencimiento,
       l.cantidad, l.proveedor, i.codigo, i.descripcion, i.categoria,
       DATEDIFF(day, GETDATE(), l.fecha_vencimiento) as dias_restantes
FROM lotes_inventario l
INNER JOIN inventario_perfiles i ON l.producto_id = i.id
WHERE l.fecha_vencimiento IS NOT NULL
  AND l.fecha_vencimiento <= ?
  AND l.fecha_vencimiento >= GETDATE()
ORDER BY l.fecha_vencimiento