-- Script para crear una nueva entrega
-- Parámetros: :codigo_entrega, :obra_id, :fecha_programada, :transportista, :vehiculo, :observaciones, :usuario_responsable
-- Retorna: ID de la entrega creada

INSERT INTO entregas (
    codigo_entrega,
    obra_id,
    fecha_programada,
    estado,
    transportista,
    vehiculo,
    observaciones,
    usuario_responsable,
    fecha_creacion,
    activo
)
VALUES (
    :codigo_entrega,
    :obra_id,
    :fecha_programada,
    'Programada',
    :transportista,
    :vehiculo,
    :observaciones,
    :usuario_responsable,
    GETDATE(),
    1
);

SELECT SCOPE_IDENTITY() as nueva_entrega_id;