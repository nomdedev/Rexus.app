INSERT INTO materiales_obra
(obra_id, etapa_id, producto_id, cantidad, estado,
 fecha_solicitud, observaciones, usuario_asignacion, fecha_asignacion)
VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, GETDATE())