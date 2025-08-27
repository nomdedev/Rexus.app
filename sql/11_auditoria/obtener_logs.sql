-- Consulta para obtener logs de auditoría
-- Parámetros: :nivel, :modulo, :usuario_id, :fecha_desde, :fecha_hasta, :accion
-- Retorna: Lista de logs filtrados

SELECT 
    l.id,
    l.fecha_hora,
    l.nivel,
    l.modulo,
    l.accion,
    l.usuario_id,
    l.detalle,
    l.ip_origen,
    l.user_agent,
    l.datos_adicionales,
    u.usuario as nombre_usuario,
    u.nombre_completo,
    CASE 
        WHEN l.nivel = 'ERROR' THEN 'Crítico'
        WHEN l.nivel = 'WARNING' THEN 'Advertencia'
        WHEN l.nivel = 'INFO' THEN 'Información'
        ELSE l.nivel
    END as tipo_evento
FROM auditoria_log l
LEFT JOIN usuarios u ON l.usuario_id = u.id
WHERE 1=1
  AND (:nivel IS NULL OR l.nivel = :nivel)
  AND (:modulo IS NULL OR l.modulo = :modulo)
  AND (:usuario_id IS NULL OR l.usuario_id = :usuario_id)
  AND (:fecha_desde IS NULL OR l.fecha_hora >= :fecha_desde)
  AND (:fecha_hasta IS NULL OR l.fecha_hora <= :fecha_hasta)
  AND (:accion IS NULL OR l.accion LIKE '%' + :accion + '%')
ORDER BY l.fecha_hora DESC;