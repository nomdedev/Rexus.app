-- Script para actualizar una obra existente
-- Parámetros: :id, :nombre, :descripcion, :estado, :fecha_inicio, :fecha_fin, :direccion
-- Retorna: Filas afectadas

UPDATE obras 
SET 
    nombre = ISNULL(:nombre, nombre),
    descripcion = ISNULL(:descripcion, descripcion),
    estado = ISNULL(:estado, estado),
    fecha_inicio = ISNULL(:fecha_inicio, fecha_inicio),
    fecha_fin = ISNULL(:fecha_fin, fecha_fin),
    direccion = ISNULL(:direccion, direccion),
    fecha_actualizacion = GETDATE()
WHERE id = :id AND activo = 1;

SELECT @@ROWCOUNT as filas_afectadas;