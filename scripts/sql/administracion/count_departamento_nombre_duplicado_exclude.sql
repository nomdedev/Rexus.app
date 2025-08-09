-- Verificar nombre de departamento duplicado excluyendo ID actual (para edición)
-- Parámetros: nombre, id_departamento_actual
SELECT COUNT(*) FROM [departamentos] WHERE LOWER(nombre) = ? AND id != ?