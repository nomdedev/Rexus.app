-- Actualizar estado de pedido
-- Archivo: actualizar_estado_pedido.sql
-- Módulo: Pedidos
-- Descripción: Actualiza el estado de un pedido con auditoría

UPDATE [pedidos] 
SET 
    estado = @nuevo_estado,
    fecha_modificacion = GETDATE(),
    usuario_aprobador = CASE 
        WHEN @nuevo_estado = 'APROBADO' THEN @usuario_id 
        ELSE usuario_aprobador 
    END,
    fecha_aprobacion = CASE 
        WHEN @nuevo_estado = 'APROBADO' THEN GETDATE() 
        ELSE fecha_aprobacion 
    END,
    motivo_cancelacion = CASE 
        WHEN @nuevo_estado = 'CANCELADO' THEN @motivo 
        ELSE motivo_cancelacion 
    END
WHERE id = @pedido_id AND activo = 1;

-- Ejemplo de uso en Python:
-- params = {
--     'pedido_id': pedido_id,
--     'nuevo_estado': 'APROBADO',
--     'usuario_id': usuario_id,
--     'motivo': None
-- }
-- cursor.execute(query, params)
