SELECT
    id, codigo, descripcion, proveedor, precio_unitario,
    unidad_medida, subcategoria, estado, observaciones,
    fecha_actualizacion
FROM productos
WHERE categoria = 'HERRAJE' AND activo = 1
ORDER BY codigo;