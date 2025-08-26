-- Buscar vidrios con filtros y paginación
SELECT id, tipo as tipo, especificaciones as especificaciones, tipo, espesor,
       proveedor, precio_m2, color, propiedades as propiedades, estado,
       dimensiones_disponibles, propiedades as observaciones
FROM vidrios
WHERE 1=1
ORDER BY fecha_creacion DESC;
