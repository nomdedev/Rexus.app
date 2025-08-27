-- Obtiene notificaciones de un usuario específico
SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion, leida, fecha_lectura
FROM notificaciones 
WHERE usuario_id = @usuario_id OR usuario_id IS NULL
ORDER BY fecha_creacion DESC
