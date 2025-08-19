SELECT
    id,
    codigo,
    tipo,
    descripcion,
    espesor,
    largo,
    ancho,
    precio,
    stock,
    stock_minimo,
    proveedor,
    activo,
    fecha_creacion,
    fecha_modificacion
FROM vidrios
WHERE id = :vidrio_id AND activo = 1;