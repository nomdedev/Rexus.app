-- select_productos_por_tipo.sql
-- Obtiene productos por tipo y opcionalmente solo activos
-- Parámetros: ? (tipo_producto)
-- Nota: Agregar condiciones adicionales via código si active_only=True

SELECT * 
FROM productos 
WHERE tipo_producto = ?
ORDER BY nombre