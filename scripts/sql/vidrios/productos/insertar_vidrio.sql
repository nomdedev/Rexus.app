INSERT INTO vidrios (
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
    fecha_creacion
) VALUES (
    :codigo,
    :tipo,
    :descripcion,
    :espesor,
    :largo,
    :ancho,
    :precio,
    :stock,
    :stock_minimo,
    :proveedor,
    1,
    GETDATE()
);