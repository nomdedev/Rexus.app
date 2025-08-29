-- sql/02_inventario/reservas/insert_reserva_fallback.sql
-- Descripción: Inserta nueva reserva usando método fallback sin utilidades base
-- Parámetros: :producto_id, :obra_id, :cantidad_reservada, :motivo, :usuario_reserva, :fecha_vencimiento
-- Retorna: ID de la nueva reserva insertada

INSERT INTO reservas_materiales (
    producto_id, 
    obra_id, 
    cantidad_reservada, 
    motivo, 
    usuario_reserva, 
    fecha_vencimiento, 
    estado, 
    fecha_creacion
) VALUES (
    :producto_id,
    :obra_id,
    :cantidad_reservada,
    :motivo,
    :usuario_reserva,
    :fecha_vencimiento,
    'ACTIVA',
    :fecha_creacion
);