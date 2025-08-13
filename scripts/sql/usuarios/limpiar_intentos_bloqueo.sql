-- Limpia intentos fallidos y bloqueo de usuario
UPDATE usuarios 
SET intentos_fallidos = 0, bloqueado_hasta = NULL 
WHERE usuario = ?