-- Obtiene configuraciones por categoría
SELECT id, clave, valor, tipo, categoria, descripcion, 
       es_editable, fecha_creacion, fecha_modificacion, 
       usuario_modificacion
FROM configuraciones 
WHERE categoria = @categoria
ORDER BY clave
