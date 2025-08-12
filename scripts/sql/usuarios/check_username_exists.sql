-- Consulta segura para verificar si un nombre de usuario ya existe
-- Utiliza la tabla 'usuarios'
-- El parámetro username se debe pasar usando prepared statements

SELECT COUNT(*) as count FROM usuarios WHERE usuario = ?;