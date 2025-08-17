-- Verificar código de departamento duplicado excluyendo ID actual (para edición)
-- Parámetros: codigo, id_departamento_actual
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(codigo) = ? AND id != ?