-- scripts/sql/logistica/obtener_obras_disponibles.sql
-- Obtiene las obras activas disponibles para asignar entregas
SELECT id, nombre, direccion, estado
FROM [obras]
WHERE activo = 1 AND estado != 'TERMINADA'
ORDER BY nombre