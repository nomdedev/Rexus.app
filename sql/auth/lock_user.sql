-- Bloquear usuario por intentos fallidos
UPDATE usuarios 
SET bloqueado_hasta = ?
WHERE usuario = ?
