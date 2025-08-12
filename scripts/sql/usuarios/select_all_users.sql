-- Consulta segura para obtener todos los usuarios
-- Utiliza la tabla 'users' o 'usuarios'
-- Los parámetros se deben pasar usando prepared statements

SELECT 
    id, username, nombre, apellido, email, rol, permisos, 
    activo, ultimo_login, fecha_creacion, fecha_actualizacion
FROM users 
WHERE activo = 1
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND rol = ?
    -- AND activo = ?
ORDER BY username;