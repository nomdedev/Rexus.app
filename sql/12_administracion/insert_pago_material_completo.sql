-- insert_pago_material_completo.sql
-- Inserta un pago de material completo
-- Parámetros: ? (producto_id), ? (proveedor_id), ? (obra_id), ? (cantidad), ? (precio_unitario), ? (total), ? (fecha_compra), ? (saldo_pendiente), ? (numero_factura), ? (observaciones), ? (usuario_creacion), ? (usuario_actualizacion)

INSERT INTO pagos_materiales
(producto_id, proveedor_id, obra_id, cantidad, precio_unitario, total,
 fecha_compra, saldo_pendiente, numero_factura, observaciones,
 usuario_creacion, usuario_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)