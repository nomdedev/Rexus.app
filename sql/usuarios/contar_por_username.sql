-- Contar usuarios por username (SQLite)  
-- Parámetros: :username
-- Retorna: COUNT de usuarios con ese username

SELECT COUNT(*) as count
FROM usuarios 
WHERE username = :username;