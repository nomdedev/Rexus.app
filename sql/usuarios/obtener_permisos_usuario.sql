-- Obtener módulos permitidos para un usuario
SELECT modulo FROM permisos_usuario
WHERE usuario_id = ?