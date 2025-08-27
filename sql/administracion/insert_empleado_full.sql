-- insert_empleado_full.sql  
-- Inserta un empleado completo con validación de tabla
-- Parámetros: ? (codigo), ? (nombre), ? (apellido), ? (documento), ? (email), ? (telefono), ? (departamento_id), ? (cargo), ? (salario), ? (fecha_ingreso), ? (usuario_creacion), ? (usuario_actualizacion)

INSERT INTO empleados
(codigo, nombre, apellido, documento, email, telefono, departamento_id,
 cargo, salario, fecha_ingreso, usuario_creacion, usuario_actualizacion)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)