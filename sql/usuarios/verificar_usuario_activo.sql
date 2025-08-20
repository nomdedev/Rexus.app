-- Verificar si usuario existe y está activo (SQLite)
-- Parámetros: :usuario_id
-- Retorna: COUNT de usuarios activos con ese ID

SELECT COUNT(*) as count
FROM usuarios 
WHERE id = :usuario_id AND activo = 1;