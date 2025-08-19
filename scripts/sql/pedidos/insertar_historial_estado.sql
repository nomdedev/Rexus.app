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