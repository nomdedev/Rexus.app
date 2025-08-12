-- Obtiene todos los vidrios con información completa
SELECT 
    v.id,
    v.codigo,
    v.tipo,
    v.descripcion,
    v.espesor,
    v.ancho,
    v.alto,
    v.area,
    v.precio,
    v.proveedor,
    v.stock,
    v.stock_minimo,
    v.activo,
    v.fecha_creacion,
    v.fecha_modificacion
FROM vidrios v
WHERE v.activo = 1
ORDER BY v.codigo;
