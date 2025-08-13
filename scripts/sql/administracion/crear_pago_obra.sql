-- Crear nuevo pago de obra
INSERT INTO pagos_obra
(obra_id, monto, fecha_pago, concepto, metodo_pago, 
 referencia, estado, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())