-- Inserción segura de nuevo pedido
-- Utiliza la tabla consolidada 'pedidos_consolidado'
-- Todos los parámetros se deben pasar usando prepared statements

INSERT INTO pedidos_consolidado (
    numero_pedido, tipo_pedido, fecha_pedido, fecha_entrega_estimada,
    cliente_id, proveedor_id, estado, prioridad, moneda,
    subtotal, descuento_porcentaje, descuento_monto, impuestos, total,
    metodo_pago, condiciones_pago, transportista, direccion_entrega,
    observaciones, aprobado_por, fecha_aprobacion,
    activo, fecha_creacion, fecha_actualizacion
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE());