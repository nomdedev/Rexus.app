-- Búsqueda avanzada de vidrios por múltiples campos
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
  AND (
    v.codigo LIKE %(termino_codigo)s
    OR v.tipo LIKE %(termino_tipo)s
    OR v.descripcion LIKE %(termino_descripcion)s
    OR v.proveedor LIKE %(termino_proveedor)s
  )
ORDER BY v.codigo;
