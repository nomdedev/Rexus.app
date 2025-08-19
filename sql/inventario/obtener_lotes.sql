-- Consulta para obtener lotes de inventario
-- Parámetros: :producto_id, :activo, :vencimiento_desde, :vencimiento_hasta
-- Retorna: Lista de lotes filtrados

SELECT 
    l.id,
    l.producto_id,
    l.numero_lote,
    l.cantidad,
    l.fecha_ingreso,
    l.fecha_vencimiento,
    l.proveedor,
    l.precio_compra,
    l.ubicacion,
    l.activo,
    ip.nombre as producto_nombre,
    ip.codigo as producto_codigo,
    CASE 
        WHEN l.fecha_vencimiento < GETDATE() THEN 'Vencido'
        WHEN l.fecha_vencimiento <= DATEADD(day, 30, GETDATE()) THEN 'Por vencer'
        ELSE 'Vigente'
    END as estado_vencimiento
FROM lotes_inventario l
INNER JOIN inventario_perfiles ip ON l.producto_id = ip.id
WHERE l.activo = ISNULL(:activo, 1)
  AND (:producto_id IS NULL OR l.producto_id = :producto_id)
  AND (:vencimiento_desde IS NULL OR l.fecha_vencimiento >= :vencimiento_desde)
  AND (:vencimiento_hasta IS NULL OR l.fecha_vencimiento <= :vencimiento_hasta)
ORDER BY l.fecha_vencimiento, ip.nombre;