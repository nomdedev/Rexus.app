-- Obtener productos con estructura estándar incluyendo stock separado (SQLite)
-- Parámetros: :search, :categoria, :activo
-- Retorna: Lista completa de productos con información de stock detallada

SELECT
    i.id,
    i.codigo,
    i.descripcion,
    i.tipo as categoria,
    COALESCE(i.acabado, '') as subcategoria,
    i.stock_actual,
    COALESCE(i.stock_minimo, 0) as stock_minimo,
    0 as stock_maximo,
    COALESCE(i.importe, 0) as precio_unitario,
    COALESCE(i.importe, 0) as precio_promedio,
    COALESCE(i.ubicacion, '') as ubicacion,
    COALESCE(i.proveedor, '') as proveedor,
    COALESCE(i.unidad, 'UND') as unidad_medida,
    'ACTIVO' as estado,
    datetime('now') as fecha_creacion,
    datetime('now') as fecha_modificacion,
    COALESCE(datetime('now'), datetime('now')) as fecha_actualizacion,
    '' as observaciones,
    COALESCE(i.qr, '') as codigo_qr,
    -- Calcular stock separado basado en reservas activas
    COALESCE(r.stock_separado, 0) as stock_separado,
    -- Stock disponible es stock actual menos stock separado
    (i.stock_actual - COALESCE(r.stock_separado, 0)) as stock_disponible,
    COALESCE(r.stock_separado, 0) as stock_reservado
FROM inventario_perfiles i
LEFT JOIN (
    -- Subconsulta para calcular stock separado por reservas
    SELECT 
        producto_id,
        SUM(cantidad_reservada) as stock_separado
    FROM reserva_materiales 
    WHERE estado = 'ACTIVA'
    GROUP BY producto_id
) r ON i.id = r.producto_id
WHERE (:search IS NULL
    OR i.codigo LIKE '%' || :search || '%'
    OR i.descripcion LIKE '%' || :search || '%'
    OR i.tipo LIKE '%' || :search || '%')
    AND (:categoria IS NULL OR i.tipo = :categoria)
    AND (:activo IS NULL OR 1 = :activo)
ORDER BY i.codigo;