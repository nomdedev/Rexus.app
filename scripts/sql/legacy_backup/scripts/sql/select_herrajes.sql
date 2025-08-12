-- Script seguro para obtener herrajes con filtros parametrizados
-- Uso: Debe ejecutarse desde el backend con parámetros seguros

SELECT
    id, codigo, descripcion, proveedor, precio_unitario,
    unidad_medida, categoria, estado, observaciones,
    fecha_actualizacion
FROM herrajes
WHERE 1=1
    -- Filtros opcionales
    -- AND proveedor LIKE ?
    -- AND codigo LIKE ?
    -- AND descripcion LIKE ?
ORDER BY codigo;
