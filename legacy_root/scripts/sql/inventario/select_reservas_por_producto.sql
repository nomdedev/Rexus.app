-- Consulta segura para obtener reservas por producto específico
-- Incluye información de la obra asociada
-- Utiliza parámetros seguros para filtrar por producto

SELECT 
    r.id,
    r.obra_id,
    r.producto_id,
    r.cantidad_reservada,
    r.fecha_reserva,
    r.fecha_liberacion,
    r.estado,
    r.usuario_id,
    r.motivo_liberacion,
    o.nombre as obra_nombre,
    o.direccion as obra_direccion
FROM reserva_materiales r
LEFT JOIN obras o ON r.obra_id = o.id
WHERE r.producto_id = ?
ORDER BY r.fecha_reserva DESC;