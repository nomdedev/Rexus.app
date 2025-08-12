-- Consulta segura para filtrado avanzado de productos
-- Utiliza parámetros seguros para todos los filtros
-- El ordenamiento se valida en el código antes de aplicarse

SELECT 
    id,
    codigo,
    descripcion,
    tipo as categoria,
    acabado as subcategoria,
    stock as stock_actual,
    stock_minimo,
    precio as precio_unitario,
    unidad_medida,
    ubicacion,
    proveedor,
    activo,
    fecha_creacion,
    fecha_modificacion
FROM inventario_perfiles
WHERE activo = 1
    -- Los filtros dinámicos se agregan en el código usando parámetros seguros:
    -- AND codigo LIKE ?
    -- AND descripcion LIKE ?
    -- AND tipo = ?
    -- AND acabado = ?
    -- AND proveedor LIKE ?
    -- AND stock >= ?
    -- AND stock <= ?
    -- AND precio >= ?
    -- AND precio <= ?
    -- ORDER BY campo_validado ASC/DESC (se agrega en código tras validación)