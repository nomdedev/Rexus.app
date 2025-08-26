-- Insertar nuevo registro de nómina
INSERT INTO nomina 
(empleado_id, mes, anio, salario_base, dias_trabajados, horas_extra,
 bonos, descuentos, faltas, bruto, total_descuentos, neto, fecha_calculo)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
