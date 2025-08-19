SELECT
    id,
    username,
    email,
    nombre_completo,
    rol,
    activo,
    intentos_fallidos,
    cuenta_bloqueada,
    ultimo_acceso,
    fecha_registro,
    fecha_modificacion
FROM usuarios
WHERE id = %(user_id)s;