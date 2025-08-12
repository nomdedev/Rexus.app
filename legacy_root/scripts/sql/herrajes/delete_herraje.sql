-- Script seguro para eliminación lógica de herraje
-- Uso: Ejecutar desde backend con parámetro seguro

UPDATE herrajes SET
    activo = 0,
    estado = 'INACTIVO',
    fecha_actualizacion = GETDATE()
WHERE id = @id;
