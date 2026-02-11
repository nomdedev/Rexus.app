-- Obtener un herraje específico por código
-- Parámetros:
--   :codigo (requerido) - Código del herraje
-- Retorna: Datos completos del herraje

SELECT codigo, nombre, descripcion, categoria, proveedor,
       precio_unitario, stock_actual, stock_minimo, unidad_medida, activo
FROM herrajes
WHERE codigo = :codigo AND activo = 1;
