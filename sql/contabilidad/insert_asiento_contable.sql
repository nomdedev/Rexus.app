-- Inserta un nuevo asiento contable
-- Parámetros: numero_asiento, fecha_asiento, tipo_asiento, concepto, referencia, debe, haber, saldo, estado, usuario_creacion
INSERT INTO libro_contable
(numero_asiento, fecha_asiento, tipo_asiento, concepto, referencia,
 debe, haber, saldo, estado, usuario_creacion, fecha_creacion, fecha_modificacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())