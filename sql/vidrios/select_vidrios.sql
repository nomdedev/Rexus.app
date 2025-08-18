-- Consulta vidrios usando columnas que existen realmente en la tabla
-- Basado en la estructura verificada: id, tipo, espesor, color, precio_m2, proveedor, especificaciones, propiedades, activo, fecha_creacion, fecha_actualizacion, dimensiones, color_acabado, stock, estado

SELECT 
    id,
    tipo,
    espesor,
    color,
    precio_m2,
    proveedor,
    especificaciones,
    propiedades,
    activo,
    fecha_creacion,
    fecha_actualizacion,
    dimensiones,
    color_acabado,
    stock,
    estado
FROM vidrios 
WHERE 1=1
-- Filtros dinámicos se agregan en el código usando parámetros seguros
