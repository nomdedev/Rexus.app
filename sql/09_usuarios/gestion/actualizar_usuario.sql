UPDATE usuarios
SET username = %(username)s,
    email = %(email)s,
    nombre_completo = %(nombre_completo)s,
    rol = %(rol)s,
    activo = %(activo)s,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE id = %(user_id)s;