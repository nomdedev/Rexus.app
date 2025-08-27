-- insert_movimiento_inventario.sql
-- Registra un movimiento de inventario
-- Parámetros: ? (producto_id), ? (tipo_movimiento), ? (cantidad), ? (stock_anterior), ? (stock_nuevo), ? (documento_referencia), ? (motivo), ? (usuario_creacion)

INSERT INTO movimientos_inventario (
    producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo,
    documento_referencia, motivo, usuario_creacion, fecha_creacion
) VALUES (
    ?, ?, ?, ?, ?,
    ?, ?, ?, GETDATE()
)