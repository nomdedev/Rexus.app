-- Crear nuevo usuario
INSERT INTO usuarios (
    username,
    password_hash,
    salt,
    email,
    nombre_completo,
    rol,
    activo,
    intentos_fallidos,
    cuenta_bloqueada,
    fecha_registro,
    fecha_modificacion
) VALUES (
    %(username)s,
    %(password_hash)s,
    %(salt)s,
    %(email)s,
    %(nombre_completo)s,
    %(rol)s,
    %(activo)s,
    0,
    0,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
