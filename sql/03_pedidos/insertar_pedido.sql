INSERT INTO [pedidos] (
    numero_pedido, cliente_id, obra_id, fecha_entrega_solicitada,
    estado, tipo_pedido, prioridad, subtotal, descuento,
    impuestos, total, observaciones, direccion_entrega,
    responsable_entrega, telefono_contacto, usuario_creador
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s
);