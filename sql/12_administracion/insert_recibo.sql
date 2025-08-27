-- Crear recibo
INSERT INTO [{tabla_recibos}] 
(numero_recibo, fecha_emision, empleado_emisor, descripcion, monto, destinatario, concepto, impreso, archivo_pdf) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
