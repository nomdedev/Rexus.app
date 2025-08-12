-- Consulta segura para obtener todos los pedidos
-- Utiliza la tabla consolidada 'pedidos_consolidado'
-- Los parámetros se deben pasar desde el código usando prepared statements

SELECT 
    p.id, p.numero_pedido, p.tipo_pedido, p.fecha_pedido, p.fecha_entrega_estimada,
    p.cliente_id, p.proveedor_id, p.estado, p.prioridad, p.moneda,
    p.subtotal, p.descuento_porcentaje, p.descuento_monto, p.impuestos, p.total,
    p.metodo_pago, p.condiciones_pago, p.transportista, p.direccion_entrega,
    p.observaciones, p.aprobado_por, p.fecha_aprobacion,
    p.activo, p.fecha_creacion, p.fecha_actualizacion
FROM pedidos_consolidado p 
WHERE p.activo = 1
    -- Filtros opcionales a agregar con parámetros seguros:
    -- AND p.estado = ?
    -- AND p.tipo_pedido = ?
    -- AND p.fecha_pedido >= ?
    -- AND p.cliente_id = ?
ORDER BY p.fecha_pedido DESC;