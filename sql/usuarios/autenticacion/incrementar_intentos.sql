UPDATE usuarios
SET intentos_fallidos = intentos_fallidos + 1,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE username = %(username)s;