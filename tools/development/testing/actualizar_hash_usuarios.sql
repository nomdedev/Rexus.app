-- Script para actualizar hash de contraseñas de usuarios de testing
-- Contraseña para todos los usuarios: test123
-- Hash SHA256: ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae

UPDATE users SET password = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae' WHERE usuario = 'admin';
UPDATE users SET password = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae' WHERE usuario = 'test_user';
UPDATE users SET password = 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae' WHERE usuario = 'operador';
INSERT INTO users (nombre, apellido, usuario, password, rol, email, activo) VALUES ('Test', 'User', 'test_user', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', 'admin', 'test@sistema.local', 1);
INSERT INTO users (nombre, apellido, usuario, password, rol, email, activo) VALUES ('Operador', 'Prueba', 'operador', 'ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae', 'usuario', 'operador@sistema.local', 1);
