-- Script para actualizar una configuración existente
-- Parámetros: :clave, :valor, :descripcion, :categoria
-- Retorna: Filas afectadas

UPDATE configuracion 
SET 
    valor = :valor,
    descripcion = ISNULL(:descripcion, descripcion),
    categoria = ISNULL(:categoria, categoria),
    fecha_actualizacion = GETDATE()
WHERE clave = :clave AND activo = 1;

-- Si no existe, crear nueva configuración
IF @@ROWCOUNT = 0
BEGIN
    INSERT INTO configuracion (
        clave,
        valor,
        descripcion,
        categoria,
        tipo_dato,
        requerido,
        activo,
        fecha_creacion
    )
    VALUES (
        :clave,
        :valor,
        ISNULL(:descripcion, 'Configuración automática'),
        ISNULL(:categoria, 'General'),
        'string',
        0,
        1,
        GETDATE()
    );
END

SELECT @@ROWCOUNT as filas_afectadas;