-- 🔒 Consulta base para listar productos del inventario
-- Reemplaza f-string vulnerable por consulta parametrizada
SELECT 
    id, 
    codigo, 
    nombre, 
    categoria, 
    tipo, 
    marca, 
    cantidad_disponible, 
    precio_unitario, 
    proveedor,
    ubicacion_almacen, 
    fecha_creacion, 
    activo
FROM inventario_perfiles
WHERE activo = 1
    AND (@categoria IS NULL OR categoria = @categoria)
    AND (@codigo IS NULL OR codigo LIKE '%' + @codigo + '%')
    AND (@nombre IS NULL OR nombre LIKE '%' + @nombre + '%')
ORDER BY fecha_creacion DESC;
