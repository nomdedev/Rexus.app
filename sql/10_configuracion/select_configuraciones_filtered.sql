SELECT id, clave, valor, tipo, categoria, descripcion, 
       es_editable, fecha_creacion, fecha_modificacion, 
       usuario_modificacion
FROM configuraciones 
WHERE 1=1
ORDER BY categoria, clave
