-- scripts/sql/logistica/actualizar_estado_entrega_con_fecha.sql
-- Actualiza el estado de una entrega añadiendo fecha de entrega
UPDATE [entregas]
SET estado = ?, fecha_entrega = GETDATE(), observaciones = ?
WHERE id = ?