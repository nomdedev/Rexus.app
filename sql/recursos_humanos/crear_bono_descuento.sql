-- Crear bono o descuento para empleado
INSERT INTO bonos_descuentos 
(empleado_id, tipo, concepto, monto, fecha_aplicacion,
 mes_aplicacion, anio_aplicacion, estado, observaciones, fecha_creacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
