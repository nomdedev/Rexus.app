-- Verificar si material está asignado a obra (SQLite)
-- Parámetros: :obra_id, :material_id
-- Retorna: COUNT de materiales asignados

SELECT COUNT(*) as count
FROM obra_materiales
WHERE obra_id = :obra_id
  AND material_id = :material_id
  AND cantidad_asignada > 0;