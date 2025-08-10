-- scripts/sql/logistica/crear_entrega.sql
-- Crea una nueva entrega
INSERT INTO [entregas]
(obra_id, transporte_id, fecha_programada, direccion_entrega,
 contacto, telefono, estado, observaciones, costo_envio,
 usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())