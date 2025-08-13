-- Búsqueda paginada optimizada de productos en inventario
-- Incluye relevancia de búsqueda y ordenamiento inteligente
-- Parámetros: search_term (4 veces), offset, limit

SELECT 
    id,
    codigo_producto,
    nombre,
    descripcion,
    categoria,
    precio_unitario,
    stock_actual,
    stock_minimo,
    unidad_medida,
    estado,
    fecha_creacion,
    fecha_actualizacion,
    -- Estado de stock calculado
    CASE 
        WHEN stock_actual <= 0 THEN 'SIN_STOCK'
        WHEN stock_actual <= stock_minimo THEN 'STOCK_BAJO'
        WHEN stock_actual <= (stock_minimo * 2) THEN 'STOCK_MEDIO'
        ELSE 'STOCK_ALTO'
    END as estado_stock,
    (precio_unitario * stock_actual) as valor_total_stock,
    -- Relevancia de búsqueda para ordenamiento
    CASE 
        WHEN codigo_producto LIKE ? THEN 1
        WHEN nombre LIKE ? THEN 2
        WHEN categoria LIKE ? THEN 3
        WHEN descripcion LIKE ? THEN 4
        ELSE 5
    END as relevancia_busqueda
FROM inventario
WHERE activo = 1
  AND (
    codigo_producto LIKE ? OR
    nombre LIKE ? OR
    categoria LIKE ? OR
    descripcion LIKE ?
  )
ORDER BY 
    relevancia_busqueda ASC,
    nombre ASC
LIMIT ? OFFSET ?;