-- Inserción segura de nuevo usuario
-- Utiliza la tabla 'usuarios'
-- Todos los parámetros se deben pasar usando prepared statements

INSERT INTO usuarios 
(usuario, password_hash, nombre_completo, email, telefono, rol, estado)
VALUES (?, ?, ?, ?, ?, ?, ?);