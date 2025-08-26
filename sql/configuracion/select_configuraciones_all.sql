-- Obtiene todas las configuraciones ordenadas por categoría y clave
SELECT id, clave, valor, tipo, categoria, descripcion, 
       activo as es_editable, fecha_creacion, fecha_modificacion, 
       'SISTEMA' as usuario_modificacion
FROM configuracion_sistema 
ORDER BY categoria, clave
