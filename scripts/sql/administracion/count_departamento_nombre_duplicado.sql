-- Verificar nombre de departamento duplicado (para creación)
-- Parámetros: nombre
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(nombre) = ?