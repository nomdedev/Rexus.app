UPDATE usuarios
SET password_hash = %(nuevo_hash)s,
    salt = %(nuevo_salt)s,
    fecha_modificacion = CURRENT_TIMESTAMP
WHERE id = %(user_id)s;