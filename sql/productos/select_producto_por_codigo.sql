-- select_producto_por_codigo.sql
-- Obtiene un producto por su código (solo activos)
-- Parámetros: ? (codigo_producto)

SELECT * 
FROM productos 
WHERE codigo = ? 
  AND activo = 1