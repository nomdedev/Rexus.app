-- Cuenta notificaciones no leídas de un usuario específico
SELECT COUNT(*) 
FROM notificaciones 
WHERE (usuario_id = @usuario_id OR usuario_id IS NULL) AND leida = @leida
