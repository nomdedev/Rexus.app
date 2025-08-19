INSERT INTO libro_contable
(numero_asiento, fecha_asiento, descripcion, debe, haber, cuenta,
 tipo_asiento, referencia, usuario_creacion, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())