-- Consulta de conteo para paginación de inventario
-- Cuenta los registros totales para el cálculo de páginas
-- Los filtros se aplican de forma segura en el código

SELECT COUNT(*) as total
FROM inventario_perfiles
WHERE activo = 1;