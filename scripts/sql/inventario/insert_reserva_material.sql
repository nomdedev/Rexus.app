INSERT INTO reserva_materiales (
    obra_id,
    producto_id,
    cantidad_reservada,
    fecha_reserva,
    estado,
    usuario_id
) VALUES (
    ?,
    ?,
    ?,
    ?,
    'ACTIVA',
    ?
);