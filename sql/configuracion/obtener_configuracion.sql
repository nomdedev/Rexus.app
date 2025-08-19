-- Consulta para obtener configuraciones del sistema
-- Parámetros: :categoria, :activo, :clave_like
-- Retorna: Lista de configuraciones filtradas

SELECT 
    c.id,
    c.clave,
    c.valor,
    c.descripcion,
    c.categoria,
    c.tipo_dato,
    c.valor_por_defecto,
    c.requerido,
    c.activo,
    c.fecha_creacion,
    c.fecha_actualizacion,
    CASE 
        WHEN c.tipo_dato = 'boolean' AND c.valor = '1' THEN 'Habilitado'
        WHEN c.tipo_dato = 'boolean' AND c.valor = '0' THEN 'Deshabilitado'
        WHEN c.requerido = 1 AND (c.valor IS NULL OR c.valor = '') THEN 'Requerido'
        ELSE 'Configurado'
    END as estado_config
FROM configuracion c
WHERE c.activo = ISNULL(:activo, 1)
  AND (:categoria IS NULL OR c.categoria = :categoria)
  AND (:clave_like IS NULL OR c.clave LIKE '%' + :clave_like + '%')
ORDER BY c.categoria, c.clave;