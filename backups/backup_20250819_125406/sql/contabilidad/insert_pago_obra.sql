INSERT INTO pagos_obra
(obra_id, concepto, categoria, monto, fecha_pago, metodo_pago,
 estado, usuario_creacion, fecha_creacion, observaciones)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)