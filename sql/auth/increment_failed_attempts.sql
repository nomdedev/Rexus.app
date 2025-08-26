-- Incrementar contador de intentos fallidos
UPDATE usuarios 
SET intentos_fallidos = intentos_fallidos + 1
WHERE usuario = ?
