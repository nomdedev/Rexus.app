-- Insertar registro en historial de estados
-- Archivo: insertar_historial_estado.sql
-- Módulo: Pedidos
-- Descripción: Registra cambio de estado para auditoría

INSERT INTO [pedidos_historial] (
    pedido_id,
    estado_anterior,
    estado_nuevo,
    usuario_id,
    observaciones
) VALUES (
    @pedido_id,
    @estado_anterior,
    @estado_nuevo,
    @usuario_id,
    @observaciones
);

-- Ejemplo de uso en Python:
-- params = {
--     'pedido_id': pedido_id,
--     'estado_anterior': estado_actual,
--     'estado_nuevo': nuevo_estado,
--     'usuario_id': usuario_id,
--     'observaciones': 'Cambio automático por sistema'
-- }
-- cursor.execute(query, params)
