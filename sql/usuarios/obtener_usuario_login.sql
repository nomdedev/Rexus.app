-- Obtener datos completos de usuario para login
-- Parámetros: username

SELECT id, username, password, nombre_completo, email,
       rol, activo, created_at, updated_at
FROM usuarios
WHERE username = ? AND activo = 1