-- Script para crear un nuevo pedido
-- Parámetros: :numero_pedido, :obra_id, :fecha_entrega_estimada, :proveedor, :total, :observaciones, :usuario_creacion
-- Retorna: ID del pedido creado

INSERT INTO pedidos (
    numero_pedido,
    obra_id,
    fecha_pedido,
    fecha_entrega_estimada,
    estado,
    total,
    proveedor,
    observaciones,
    usuario_creacion,
    fecha_creacion,
    activo
)
VALUES (
    :numero_pedido,
    :obra_id,
    GETDATE(),
    :fecha_entrega_estimada,
    'Pendiente',
    ISNULL(:total, 0),
    :proveedor,
    :observaciones,
    :usuario_creacion,
    GETDATE(),
    1
);

SELECT SCOPE_IDENTITY() as nuevo_pedido_id;