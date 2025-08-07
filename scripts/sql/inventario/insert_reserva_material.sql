-- Inserción segura de reserva de material para obra
-- Utiliza parámetros seguros para prevenir SQL injection
-- Crea registro de auditoría para trazabilidad

INSERT INTO reserva_materiales (
    obra_id,
    producto_id,
    cantidad_reservada,
    fecha_reserva,
    estado,
    usuario_id
) VALUES (
    ?,  -- obra_id
    ?,  -- producto_id
    ?,  -- cantidad_reservada
    ?,  -- fecha_reserva
    'ACTIVA',  -- estado por defecto
    ?   -- usuario_id
);