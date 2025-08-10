-- Consulta segura para obtener productos paginados
-- Utiliza parámetros para OFFSET y LIMIT
-- Los filtros se aplican de forma segura mediante parámetros

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
ORDER BY id DESC
OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;