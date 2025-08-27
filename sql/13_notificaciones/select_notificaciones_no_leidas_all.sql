-- Obtiene todas las notificaciones no leídas
SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion
FROM notificaciones 
WHERE leida = @leida
ORDER BY fecha_creacion DESC
