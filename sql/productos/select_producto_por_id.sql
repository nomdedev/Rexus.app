-- select_producto_por_id.sql
-- Obtiene un producto por su ID (solo activos)
-- Parámetros: ? (producto_id)

SELECT * 
FROM productos 
WHERE id = ? 
  AND activo = 1