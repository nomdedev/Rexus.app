-- Consulta segura para obtener reservas de materiales por obra
-- Incluye información del producto y estado de la reserva
-- Utiliza parámetros seguros para filtrar por obra

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
    i.codigo as producto_codigo,
    i.descripcion as producto_descripcion,
    i.tipo as producto_categoria,
    i.precio as precio_unitario,
    i.unidad_medida
FROM reserva_materiales r
INNER JOIN inventario_perfiles i ON r.producto_id = i.id
WHERE r.obra_id = ?
ORDER BY r.fecha_reserva DESC;