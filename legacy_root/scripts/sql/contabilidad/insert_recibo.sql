-- Inserta un nuevo recibo
-- Parámetros: numero_recibo, fecha_emision, tipo_recibo, concepto, beneficiario, monto, moneda, estado, impreso, usuario_creacion
INSERT INTO recibos
(numero_recibo, fecha_emision, tipo_recibo, concepto, beneficiario,
 monto, moneda, estado, impreso, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())