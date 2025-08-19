SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto,
    o.direccion
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE (
    o.nombre LIKE ? OR
    o.descripcion LIKE ? OR
    c.nombre LIKE ? OR
    o.direccion LIKE ?
)
ORDER BY o.fecha_inicio DESC;
SELECT
    COUNT(*) AS total_obras,
    COUNT(CASE WHEN estado = 'activa' THEN 1 END) AS obras_activas,
    COUNT(CASE WHEN estado = 'completada' THEN 1 END) AS obras_completadas,
    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) AS obras_canceladas,
    COUNT(CASE WHEN estado = 'planificada' THEN 1 END) AS obras_planificadas,
    AVG(presupuesto) AS presupuesto_promedio,
    SUM(presupuesto) AS presupuesto_total,
    AVG(costo_real) AS costo_real_promedio,
    SUM(costo_real) AS costo_real_total
FROM obras
WHERE deleted_at IS NULL;
SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto,
    o.direccion
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE 1=1
ORDER BY o.fecha_inicio DESC
OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
SELECT COUNT(*) AS total_count
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE 1=1;
SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    DATEDIFF(day, o.fecha_fin_estimada, GETDATE()) AS dias_vencidos,
    o.presupuesto
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE o.fecha_fin_estimada < GETDATE()
  AND o.estado NOT IN ('completada', 'cancelada')
ORDER BY o.fecha_fin_estimada ASC;
SELECT
    FORMAT(o.fecha_inicio, 'yyyy-MM') AS periodo,
    COUNT(*) AS obras_iniciadas,
    COUNT(CASE WHEN o.fecha_fin_real IS NOT NULL THEN 1 END) AS obras_completadas,
    AVG(DATEDIFF(day, o.fecha_inicio, ISNULL(o.fecha_fin_real, GETDATE()))) AS duracion_promedio_dias,
    SUM(o.presupuesto) AS presupuesto_total,
    SUM(o.costo_real) AS costo_real_total,
    CASE
        WHEN SUM(o.presupuesto) > 0 THEN
            ((SUM(o.presupuesto) - SUM(COALESCE(o.costo_real, 0))) / SUM(o.presupuesto) * 100)
        ELSE 0
    END AS margen_promedio_porcentaje
FROM obras o
WHERE o.fecha_inicio BETWEEN ? AND ?
GROUP BY DATE_FORMAT(o.fecha_inicio, '%Y-%m')
ORDER BY periodo DESC;
SELECT
    c.id AS cliente_id,
    c.nombre AS cliente_nombre,
    COUNT(o.id) AS total_obras,
    COUNT(CASE WHEN o.estado = 'completada' THEN 1 END) AS obras_completadas,
    SUM(o.presupuesto) AS presupuesto_total,
    SUM(o.costo_real) AS costo_real_total,
    AVG(o.presupuesto) AS presupuesto_promedio
FROM clientes c
LEFT JOIN obras o ON c.id = o.cliente_id
GROUP BY c.id, c.nombre
HAVING COUNT(o.id) > 0
ORDER BY total_obras DESC;
SELECT
    c.id AS cliente_id,
    c.nombre AS cliente_nombre,
    COUNT(o.id) AS total_obras,
    SUM(o.presupuesto) AS facturacion_total,
    AVG(o.presupuesto) AS ticket_promedio
FROM clientes c
INNER JOIN obras o ON c.id = o.cliente_id
WHERE o.estado = 'completada'
GROUP BY c.id, c.nombre
ORDER BY facturacion_total DESC
LIMIT 10;
SELECT
    o.id,
    o.nombre,
    o.presupuesto,
    o.costo_real,
    (o.presupuesto - COALESCE(o.costo_real, 0)) AS ganancia,
    CASE
        WHEN o.presupuesto > 0 THEN
            ((o.presupuesto - COALESCE(o.costo_real, 0)) / o.presupuesto * 100)
        ELSE 0
    END AS margen_porcentaje,
    o.estado,
    c.nombre AS cliente_nombre
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE o.estado = 'completada'
ORDER BY margen_porcentaje DESC;
SELECT
    o.id,
    o.nombre,
    o.descripcion,
    o.cliente_id,
    c.nombre AS cliente_nombre,
    o.estado,
    o.fecha_inicio,
    o.fecha_fin_estimada,
    o.presupuesto,
    o.direccion,
    DATEDIFF(COALESCE(o.fecha_fin_real, NOW()), o.fecha_inicio) AS duracion_dias
FROM obras o
LEFT JOIN clientes c ON o.cliente_id = c.id
WHERE o.estado = ?
ORDER BY o.fecha_inicio DESC;
SELECT
    'obras_totales' AS metrica,
    COUNT(*) AS valor
FROM obras
WHERE deleted_at IS NULL
UNION ALL
SELECT
    'obras_activas' AS metrica,
    COUNT(*) AS valor
FROM obras
WHERE estado = 'activa' AND deleted_at IS NULL
UNION ALL
SELECT
    'obras_vencidas' AS metrica,
    COUNT(*) AS valor
FROM obras
WHERE fecha_fin_estimada < NOW()
  AND estado NOT IN ('completada', 'cancelada')
  AND deleted_at IS NULL
UNION ALL
SELECT
    'presupuesto_total' AS metrica,
    COALESCE(SUM(presupuesto), 0) AS valor
FROM obras
WHERE estado = 'activa' AND deleted_at IS NULL;
SELECT
    YEARWEEK(o.fecha_inicio) AS semana,
    COUNT(*) AS obras_iniciadas,
    COUNT(CASE WHEN o.fecha_fin_real IS NOT NULL
               AND YEARWEEK(o.fecha_fin_real) = YEARWEEK(o.fecha_inicio)
          THEN 1 END) AS obras_completadas_misma_semana
FROM obras o
WHERE o.fecha_inicio >= DATE_SUB(NOW(), INTERVAL 12 WEEK)
GROUP BY YEARWEEK(o.fecha_inicio)
ORDER BY semana DESC;
SELECT
    o.id,
    o.nombre,
    o.presupuesto,
    DATEDIFF(COALESCE(o.fecha_fin_real, NOW()), o.fecha_inicio) AS duracion_dias,
    CASE
        WHEN DATEDIFF(COALESCE(o.fecha_fin_real, NOW()), o.fecha_inicio) > 0 THEN
            (o.presupuesto / DATEDIFF(COALESCE(o.fecha_fin_real, NOW()), o.fecha_inicio))
        ELSE 0
    END AS presupuesto_por_dia
FROM obras o
WHERE o.fecha_inicio IS NOT NULL
ORDER BY presupuesto_por_dia DESC;
SELECT
    'vencimiento_proximo' AS tipo_alerta,
    o.id,
    o.nombre,
    o.fecha_fin_estimada,
    DATEDIFF(o.fecha_fin_estimada, NOW()) AS dias_restantes
FROM obras o
WHERE o.fecha_fin_estimada BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
  AND o.estado NOT IN ('completada', 'cancelada')
UNION ALL
SELECT
    'presupuesto_excedido' AS tipo_alerta,
    o.id,
    o.nombre,
    o.fecha_fin_estimada,
    NULL AS dias_restantes
FROM obras o
WHERE o.costo_real > o.presupuesto
  AND o.estado = 'activa'
ORDER BY tipo_alerta, dias_restantes ASC;