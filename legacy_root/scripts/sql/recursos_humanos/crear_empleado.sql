INSERT INTO empleados
(codigo, nombre, apellido, dni, telefono, email, direccion,
 fecha_nacimiento, fecha_ingreso, salario_base, cargo, 
 departamento_id, estado, activo, fecha_creacion, fecha_modificacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, GETDATE(), GETDATE())