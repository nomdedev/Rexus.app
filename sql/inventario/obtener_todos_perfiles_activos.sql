-- Obtener todos los perfiles de inventario activos
SELECT 
    id, codigo, descripcion, tipo, proveedor, stock, precio, 
    stock_minimo, stock_maximo, ubicacion, observaciones, 
    fecha_creacion
FROM inventario_perfiles 
WHERE activo = 1
ORDER BY codigo