-- Inserta una nueva configuración
INSERT INTO configuracion_sistema 
(clave, valor, tipo, categoria, descripcion, activo)
VALUES (@clave, @valor, @tipo, @categoria, @descripcion, @es_editable)
