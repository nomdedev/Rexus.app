-- select_notificaciones_usuario_base.sql
-- Query base para obtener notificaciones de un usuario (filtros dinámicos se agregan en código)
-- Parámetros: ? (usuario_id)

SELECT n.id, n.titulo, n.mensaje, n.tipo, n.prioridad,
       n.modulo_origen, n.fecha_creacion, n.fecha_expiracion,
       un.leida, un.fecha_lectura, un.archivada
FROM notificaciones n
LEFT JOIN usuarios_notificaciones un ON n.id = un.notificacion_id
WHERE (un.usuario_id = ? OR un.usuario_id IS NULL)
  AND n.activa = 1
  AND (n.fecha_expiracion IS NULL OR n.fecha_expiracion > GETDATE())