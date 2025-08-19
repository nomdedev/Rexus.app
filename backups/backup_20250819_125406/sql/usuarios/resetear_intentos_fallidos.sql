UPDATE intentos_login
SET exitoso = NULL
WHERE username = ? AND exitoso = 0