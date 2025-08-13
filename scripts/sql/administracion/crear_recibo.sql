-- Crear nuevo recibo
INSERT INTO recibos
(numero_recibo, fecha_recibo, cliente, concepto, monto, 
 metodo_pago, referencia_pago, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())