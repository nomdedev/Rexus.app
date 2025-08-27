-- Validar departamento duplicado por nombre  
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(nombre) = ?
