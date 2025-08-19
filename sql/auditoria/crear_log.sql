-- Script para crear un nuevo log de auditoría
-- Parámetros: :nivel, :modulo, :accion, :usuario_id, :detalle, :ip_origen, :user_agent, :datos_adicionales
-- Retorna: ID del log creado

INSERT INTO auditoria_log (
    fecha_hora,
    nivel,
    modulo,
    accion,
    usuario_id,
    detalle,
    ip_origen,
    user_agent,
    datos_adicionales
)
VALUES (
    GETDATE(),
    :nivel,
    :modulo,
    :accion,
    :usuario_id,
    :detalle,
    :ip_origen,
    :user_agent,
    :datos_adicionales
);

SELECT SCOPE_IDENTITY() as nuevo_log_id;