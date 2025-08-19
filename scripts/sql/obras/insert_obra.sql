INSERT INTO obras
(codigo, nombre, descripcion, cliente, direccion, telefono_contacto,
 fecha_inicio, fecha_fin_estimada, presupuesto_total,
 estado, tipo_obra, prioridad, responsable, observaciones,
 usuario_creacion, activo, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())