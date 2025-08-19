-- Consulta para obtener entregas de logística
-- Parámetros: :estado, :obra_id, :fecha_desde, :fecha_hasta, :activo
-- Retorna: Lista de entregas filtradas

SELECT 
    e.id,
    e.codigo_entrega,
    e.obra_id,
    e.fecha_programada,
    e.fecha_real,
    e.estado,
    e.transportista,
    e.vehiculo,
    e.observaciones,
    e.usuario_responsable,
    e.fecha_creacion,
    e.activo,
    ISNULL(o.nombre, 'Sin asignar') as obra_nombre,
    ISNULL(t.codigo, 'Sin asignar') as transporte_codigo,
    CASE 
        WHEN e.fecha_programada < GETDATE() AND e.estado != 'Entregada' THEN 'Atrasada'
        WHEN e.estado = 'Entregada' THEN 'Completada'
        ELSE e.estado
    END as estado_actual
FROM entregas e
LEFT JOIN obras o ON e.obra_id = o.id
LEFT JOIN transportes t ON e.transportista = t.nombre
WHERE e.activo = ISNULL(:activo, 1)
  AND (:estado IS NULL OR e.estado = :estado)
  AND (:obra_id IS NULL OR e.obra_id = :obra_id)
  AND (:fecha_desde IS NULL OR e.fecha_programada >= :fecha_desde)
  AND (:fecha_hasta IS NULL OR e.fecha_programada <= :fecha_hasta)
ORDER BY e.fecha_programada DESC;