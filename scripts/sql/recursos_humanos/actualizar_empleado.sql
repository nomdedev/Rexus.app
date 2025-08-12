UPDATE empleados
SET nombre = ?, apellido = ?, dni = ?, telefono = ?, email = ?, 
    direccion = ?, fecha_nacimiento = ?, salario_base = ?, 
    cargo = ?, departamento_id = ?, estado = ?, fecha_modificacion = GETDATE()
WHERE id = ?