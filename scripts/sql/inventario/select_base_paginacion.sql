-- Consulta base para paginación de inventario
-- Utiliza la tabla principal de inventario_perfiles
-- Los filtros y ordenamiento se aplican de forma segura en el código

SELECT 
    id,
    codigo,
    descripcion,
    tipo as categoria,
    acabado as subcategoria,
    stock as stock_actual,
    precio as precio_unitario,
    activo,
    fecha_creacion,
    fecha_modificacion
FROM inventario_perfiles
WHERE activo = 1;