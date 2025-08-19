SELECT id, codigo, descripcion, proveedor, precio_unitario, unidad_medida, subcategoria, estado
FROM productos
WHERE (codigo LIKE @termino OR descripcion LIKE @termino OR proveedor LIKE @termino)
  AND categoria = 'HERRAJE'
  AND estado = 'ACTIVO'
ORDER BY codigo;