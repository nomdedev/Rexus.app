-- Obtener todos los vidrios con información de stock
SELECT 
    v.id,
    v.codigo_vidrio,
    v.descripcion,
    v.espesor,
    v.ancho,
    v.alto,
    v.tipo_vidrio,
    v.color,
    v.precio_m2,
    v.stock_actual,
    v.stock_minimo,
    v.ubicacion_almacen,
    v.proveedor_principal,
    v.fecha_creacion,
    v.fecha_actualizacion,
    v.usuario_creacion,
    v.estado
FROM vidrios v
WHERE v.estado = 'ACTIVO'
ORDER BY v.descripcion