-- Crear asiento contable
INSERT INTO [{tabla_libro_contable}] 
(numero_asiento, fecha_asiento, descripcion, cuenta, debe, haber, saldo, empleado_id) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
