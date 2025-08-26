-- Cuenta todas las notificaciones no leídas
SELECT COUNT(*) 
FROM notificaciones 
WHERE leida = @leida
