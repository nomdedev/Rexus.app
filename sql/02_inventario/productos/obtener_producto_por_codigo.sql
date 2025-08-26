SELECT
    id,
    codigo,
    descripcion,
    categoria,
    unidad_medida,
    precio_compra,
    precio_venta,
    stock_actual,
    stock_minimo,
    ubicacion,
    observaciones,
    qr_data,
    fecha_creacion,
    fecha_modificacion
FROM [inventario]
WHERE LOWER(codigo) = LOWER(@codigo) AND activo = 1;