-- Consulta optimizada para obtener productos de inventario paginados
-- Optimizada para tablas grandes con índices apropiados
-- Parámetros: offset, limit

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
    -- Campos calculados para mejor UX
    CASE 
        WHEN stock_actual <= 0 THEN 'SIN_STOCK'
        WHEN stock_actual <= stock_minimo THEN 'STOCK_BAJO'
        WHEN stock_actual <= (stock_minimo * 2) THEN 'STOCK_MEDIO'
        ELSE 'STOCK_ALTO'
    END as estado_stock,
    (precio_unitario * stock_actual) as valor_total_stock
FROM inventario
WHERE activo = 1
ORDER BY nombre ASC
LIMIT ? OFFSET ?;