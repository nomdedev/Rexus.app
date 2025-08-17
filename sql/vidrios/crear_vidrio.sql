-- Crear nuevo vidrio en inventario
INSERT INTO vidrios (
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
    usuario_creacion,
    fecha_creacion,
    fecha_actualizacion,
    estado
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), 'ACTIVO')