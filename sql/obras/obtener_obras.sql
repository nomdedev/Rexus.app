-- Consulta para obtener obras con filtros opcionales
-- Parámetros: :estado, :cliente_like, :activo, :fecha_desde, :fecha_hasta
-- Retorna: Lista de obras filtradas

SELECT 
    o.id,
    o.nombre,
    o.descripcion,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin,
    o.direccion as ubicacion,
    o.fecha_creacion,
    o.activo,
    CASE 
        WHEN o.fecha_fin < GETDATE() AND o.estado != 'Completada' THEN 'Atrasada'
        WHEN o.estado = 'Completada' THEN 'Finalizada'
        WHEN o.estado = 'En progreso' THEN 'Activa'
        ELSE o.estado
    END as estado_actual
FROM obras o
WHERE o.activo = ISNULL(:activo, 1)
  AND (:estado IS NULL OR o.estado = :estado)
  AND (:cliente_like IS NULL OR o.descripcion LIKE '%' + :cliente_like + '%')
  AND (:fecha_desde IS NULL OR o.fecha_inicio >= :fecha_desde)
  AND (:fecha_hasta IS NULL OR o.fecha_fin <= :fecha_hasta)
ORDER BY o.fecha_creacion DESC;