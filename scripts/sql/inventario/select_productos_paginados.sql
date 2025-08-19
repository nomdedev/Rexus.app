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
ORDER BY id DESC
OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;