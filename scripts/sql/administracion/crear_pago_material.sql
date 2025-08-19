INSERT INTO pagos_materiales
(proveedor_id, monto, fecha_pago, concepto, metodo_pago,
 referencia, estado, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())