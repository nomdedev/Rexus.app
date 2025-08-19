UPDATE vidrios
SET
    codigo = :codigo,
    tipo = :tipo,
    descripcion = :descripcion,
    espesor = :espesor,
    largo = :largo,
    ancho = :ancho,
    precio = :precio,
    stock = :stock,
    stock_minimo = :stock_minimo,
    proveedor = :proveedor,
    fecha_modificacion = GETDATE()
WHERE id = :vidrio_id AND activo = 1;