-- Insertar registro de intento de login
-- Parámetros: username, exitoso (1 para éxito, 0 para fallo)

INSERT INTO intentos_login (username, exitoso, fecha_intento)
VALUES (?, ?, GETDATE())