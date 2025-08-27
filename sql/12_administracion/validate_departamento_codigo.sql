-- Validar departamento duplicado por código
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(codigo) = ?
