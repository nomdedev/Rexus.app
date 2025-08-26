INSERT INTO asistencias
(empleado_id, fecha, hora_entrada, hora_salida, horas_trabajadas,
 horas_extra, tipo, observaciones, fecha_registro)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
