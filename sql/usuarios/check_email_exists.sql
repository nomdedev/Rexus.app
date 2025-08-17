-- Consulta segura para verificar si un email ya existe
-- Utiliza la tabla 'usuarios'
-- El parámetro email se debe pasar usando prepared statements

SELECT COUNT(*) as count FROM usuarios WHERE email = ?;