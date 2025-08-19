INSERT INTO pedidos (
    numero_pedido,
    cliente_id,
    obra_id,
    fecha_entrega_solicitada,
    tipo_pedido,
    prioridad,
    observaciones,
    direccion_entrega,
    responsable_entrega,
    telefono_contacto,
    usuario_creador
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);