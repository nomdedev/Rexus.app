-- Obtiene todas las notificaciones
SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion, leida, fecha_lectura
FROM notificaciones 
ORDER BY fecha_creacion DESC
