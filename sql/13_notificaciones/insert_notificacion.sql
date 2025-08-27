-- Inserta una nueva notificación
INSERT INTO notificaciones (titulo, mensaje, tipo, usuario_id, fecha_creacion, leida)
VALUES (@titulo, @mensaje, @tipo, @usuario_id, @fecha_creacion, @leida)
