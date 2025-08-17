-- Verificar código de departamento duplicado (para creación)
-- Parámetros: codigo
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(codigo) = ?