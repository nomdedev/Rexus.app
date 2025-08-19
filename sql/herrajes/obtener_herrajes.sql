-- Consulta para obtener herrajes disponibles
-- Parámetros: :categoria, :proveedor, :activo, :stock_minimo, :nombre_like
-- Retorna: Lista de herrajes filtrados

SELECT 
    h.id,
    h.codigo,
    h.nombre,
    h.descripcion,
    h.categoria,
    h.proveedor,
    h.precio_unitario,
    h.stock_actual,
    h.stock_minimo,
    h.unidad_medida,
    h.especificaciones,
    h.imagen_url,
    h.activo,
    h.fecha_creacion,
    h.fecha_actualizacion,
    h.estado,
    h.observaciones,
    CASE 
        WHEN h.stock_actual <= h.stock_minimo THEN 'Stock Bajo'
        WHEN h.stock_actual = 0 THEN 'Sin Stock'
        ELSE 'Disponible'
    END as estado_stock
FROM herrajes h
WHERE h.activo = ISNULL(:activo, 1)
  AND (:categoria IS NULL OR h.categoria = :categoria)
  AND (:proveedor IS NULL OR h.proveedor LIKE '%' + :proveedor + '%')
  AND (:stock_minimo IS NULL OR h.stock_actual >= :stock_minimo)
  AND (:nombre_like IS NULL OR h.nombre LIKE '%' + :nombre_like + '%')
ORDER BY h.categoria, h.nombre;