-- Obtiene notificaciones no leídas de un usuario específico
SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion
FROM notificaciones 
WHERE (usuario_id = @usuario_id OR usuario_id IS NULL) AND leida = @leida
ORDER BY fecha_creacion DESC
