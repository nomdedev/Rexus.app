-- insertar_movimiento_inventario.sql
-- Inserta un nuevo movimiento de inventario
-- Parámetros: ? (producto_id), ? (tipo_movimiento), ? (cantidad), ? (stock_anterior), ? (stock_nuevo), ? (observaciones), ? (obra_id), ? (usuario)

INSERT INTO movimientos_inventario (
    producto_id, tipo_movimiento, cantidad, stock_anterior,
    stock_nuevo, observaciones, obra_id, usuario, fecha_movimiento
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())