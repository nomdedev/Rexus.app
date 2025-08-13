-- Obtener registros del libro contable
-- Parámetros opcionales para filtrado
SELECT 
    id,
    numero_asiento,
    fecha_asiento,
    descripcion,
    debe,
    haber,
    cuenta,
    tipo_asiento,
    referencia,
    usuario_creacion,
    fecha_creacion
FROM libro_contable
WHERE 1=1