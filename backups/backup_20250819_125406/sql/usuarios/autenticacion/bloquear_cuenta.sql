UPDATE usuarios
SET cuenta_bloqueada = 1,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE username = %(username)s;