-- select_productos_por_tipo_activos.sql
-- Obtiene productos por tipo que estén activos
-- Parámetros: ? (tipo_producto)

SELECT * 
FROM productos 
WHERE tipo_producto = ?
  AND activo = 1 
  AND estado = 'ACTIVO'
ORDER BY nombre