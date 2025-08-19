-- Consulta para obtener todos los vidrios disponibles
-- Parámetros: :tipo, :proveedor, :espesor_min, :espesor_max, :activo
-- Retorna: Lista completa de vidrios con filtros opcionales

SELECT 
    v.id,
    v.tipo,
    v.espesor,
    v.color,
    v.precio_m2,
    v.proveedor,
    v.especificaciones,
    v.propiedades,
    v.activo,
    v.fecha_creacion,
    v.fecha_actualizacion,
    v.dimensiones,
    v.color_acabado,
    v.stock,
    v.estado,
    CASE 
        WHEN v.stock > 0 THEN 'Disponible'
        ELSE 'Sin stock'
    END as disponibilidad
FROM vidrios v
WHERE v.activo = ISNULL(:activo, 1)
  AND (:tipo IS NULL OR v.tipo LIKE '%' + :tipo + '%')
  AND (:proveedor IS NULL OR v.proveedor LIKE '%' + :proveedor + '%')
  AND (:espesor_min IS NULL OR v.espesor >= :espesor_min)
  AND (:espesor_max IS NULL OR v.espesor <= :espesor_max)
ORDER BY v.tipo, v.espesor, v.color;