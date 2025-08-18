-- Resetear intentos fallidos marcándolos como obsoletos
-- Parámetros: username

UPDATE intentos_login
SET exitoso = NULL
WHERE username = ? AND exitoso = 0