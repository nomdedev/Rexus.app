-- Consulta para obtener compras con filtros
-- Parámetros: :estado, :proveedor, :fecha_desde, :fecha_hasta, :activo
-- Retorna: Lista de compras filtradas

SELECT 
    c.id,
    c.numero_compra,
    c.proveedor_id,
    c.fecha_compra,
    c.fecha_entrega,
    c.estado,
    c.total,
    c.descuento,
    c.impuestos,
    c.total_final,
    c.observaciones,
    c.usuario_creacion,
    c.fecha_creacion,
    c.activo,
    p.nombre as proveedor_nombre,
    p.contacto as proveedor_contacto,
    CASE 
        WHEN c.fecha_entrega < GETDATE() AND c.estado != 'Entregada' THEN 'Atrasada'
        WHEN c.estado = 'Entregada' THEN 'Completada'
        ELSE c.estado
    END as estado_actual
FROM compras c
LEFT JOIN proveedores p ON c.proveedor_id = p.id
WHERE c.activo = ISNULL(:activo, 1)
  AND (:estado IS NULL OR c.estado = :estado)
  AND (:proveedor IS NULL OR p.nombre LIKE '%' + :proveedor + '%')
  AND (:fecha_desde IS NULL OR c.fecha_compra >= :fecha_desde)
  AND (:fecha_hasta IS NULL OR c.fecha_compra <= :fecha_hasta)
ORDER BY c.fecha_creacion DESC;