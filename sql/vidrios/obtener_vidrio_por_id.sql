-- Obtener vidrio específico por ID
SELECT 
    id,
    codigo_vidrio,
    descripcion,
    espesor,
    ancho,
    alto,
    tipo_vidrio,
    color,
    precio_m2,
    stock_actual,
    stock_minimo,
    ubicacion_almacen,
    proveedor_principal,
    fecha_creacion,
    fecha_actualizacion,
    usuario_creacion,
    estado
FROM vidrios 
WHERE id = ? AND estado = 'ACTIVO'