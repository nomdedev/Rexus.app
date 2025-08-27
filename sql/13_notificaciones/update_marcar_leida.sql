-- Marca una notificación como leída
UPDATE notificaciones 
SET leida = @leida, fecha_lectura = @fecha_lectura
WHERE id = @notificacion_id
