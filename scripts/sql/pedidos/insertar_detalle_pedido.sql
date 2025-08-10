-- Insertar detalle de pedido
-- Archivo: insertar_detalle_pedido.sql

INSERT INTO pedidos_detalle (
    pedido_id, 
    producto_id, 
    codigo_producto, 
    descripcion,
    categoria, 
    cantidad, 
    unidad_medida, 
    precio_unitario,
    descuento_item, 
    subtotal_item, 
    observaciones_item
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
