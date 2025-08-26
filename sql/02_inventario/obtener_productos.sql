-- Consulta para obtener productos de inventario
-- Parámetros: :categoria, :activo, :stock_minimo, :nombre_like
-- Retorna: Lista de productos filtrados

SELECT 
    ip.id,
    ip.codigo,
    ip.nombre,
    ip.descripcion,
    ip.categoria,
    ip.unidad_medida,
    ip.precio_unitario,
    ip.stock_actual,
    ip.stock_minimo,
    ip.proveedor,
    ip.fecha_creacion,
    ip.activo,
    CASE 
        WHEN ip.stock_actual <= ip.stock_minimo THEN 'Stock Bajo'
        WHEN ip.stock_actual = 0 THEN 'Sin Stock'
        ELSE 'Disponible'
    END as estado_stock
FROM inventario_perfiles ip
WHERE ip.activo = ISNULL(:activo, 1)
  AND (:categoria IS NULL OR ip.categoria = :categoria)
  AND (:stock_minimo IS NULL OR ip.stock_actual >= :stock_minimo)
  AND (:nombre_like IS NULL OR ip.nombre LIKE '%' + :nombre_like + '%')
ORDER BY ip.nombre, ip.codigo;