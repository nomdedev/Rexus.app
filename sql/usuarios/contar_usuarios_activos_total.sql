-- Contar usuarios activos (SQLite)
-- Parámetros: ninguno
-- Retorna: COUNT de usuarios activos

SELECT COUNT(*) as usuarios_activos
FROM usuarios 
WHERE activo = 1;