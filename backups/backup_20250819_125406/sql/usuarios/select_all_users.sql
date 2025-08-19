SELECT
    id, username, nombre, apellido, email, rol, permisos,
    activo, ultimo_login, fecha_creacion, fecha_actualizacion
FROM users
WHERE activo = 1
ORDER BY username;