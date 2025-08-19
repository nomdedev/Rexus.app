SELECT
    u.id,
    u.username,
    u.password_hash,
    u.salt,
    u.email,
    u.rol,
    u.activo,
    u.intentos_fallidos,
    u.cuenta_bloqueada,
    u.ultimo_acceso,
    u.fecha_registro,
    u.fecha_modificacion
FROM usuarios u
WHERE u.username = %(username)s
    AND u.activo = 1
    AND u.cuenta_bloqueada = 0
LIMIT 1;