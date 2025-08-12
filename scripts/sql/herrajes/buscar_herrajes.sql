SELECT id, codigo, descripcion, proveedor, precio_unitario, unidad_medida, categoria, estado
FROM herrajes
WHERE (codigo LIKE @termino OR descripcion LIKE @termino OR proveedor LIKE @termino)
  AND estado = 'ACTIVO'
ORDER BY codigo;
