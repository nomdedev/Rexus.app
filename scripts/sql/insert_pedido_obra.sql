-- Script seguro para crear pedido de herrajes para una obra
-- Uso: Ejecutar desde backend con parámetros seguros

INSERT INTO pedidos_herrajes (
    obra_id, proveedor, fecha_pedido, estado, total_estimado
) VALUES (
    @obra_id, @proveedor, GETDATE(), 'PENDIENTE', @total_estimado
);
