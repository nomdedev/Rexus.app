-- Actualiza el contador de intentos fallidos y bloquea usuario
UPDATE usuarios 
SET intentos_fallidos = ?, bloqueado_hasta = ? 
WHERE usuario = ?