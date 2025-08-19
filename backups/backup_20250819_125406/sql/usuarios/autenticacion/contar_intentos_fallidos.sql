SELECT COUNT(*) FROM intentos_login
WHERE username = ? AND exitoso = 0 AND fecha_intento > ?