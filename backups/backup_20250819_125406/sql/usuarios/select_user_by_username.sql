SELECT
    id, username, password_hash, nombre, apellido, email,
    rol, permisos, activo, ultimo_login,
    fecha_creacion, fecha_actualizacion
FROM users
WHERE username = ? AND activo = 1;