-- Cerrar todas las sesiones activas de un usuario
UPDATE sesiones_usuario
SET activa = 0, fecha_fin = GETDATE()
WHERE usuario_id = ? AND activa = 1