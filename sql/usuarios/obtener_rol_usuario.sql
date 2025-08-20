-- Obtener rol de usuario activo (SQLite)
-- Parámetros: :usuario_id
-- Retorna: rol del usuario si está activo

SELECT rol
FROM usuarios
WHERE id = :usuario_id AND activo = 1;