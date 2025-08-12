INSERT INTO historial_laboral
(empleado_id, tipo, descripcion, fecha, valor_anterior, valor_nuevo, usuario_creacion)
VALUES (?, ?, ?, GETDATE(), ?, ?, 'SYSTEM')