-- Consultas SQL optimizadas para gestión de recursos de obras
-- Archivo: recursos_obras_optimizado.sql

-- Consulta optimizada para obtener materiales de una obra (separada por tipo)
-- Vidrios de obra
SELECT 
    om.id,
    om.obra_id,
    om.material_id,
    'vidrio' AS tipo_material,
    om.cantidad,
    om.cantidad_utilizada,
    om.fecha_asignacion,
    v.tipo AS nombre_material,
    v.precio_m2 AS precio_unitario
FROM obra_materiales om
INNER JOIN vidrios v ON om.material_id = v.id
WHERE om.obra_id = ? AND om.tipo_material = 'vidrio';

-- Inventario de obra  
SELECT 
    om.id,
    om.obra_id,
    om.material_id,
    'inventario' AS tipo_material,
    om.cantidad,
    om.cantidad_utilizada,
    om.fecha_asignacion,
    i.nombre AS nombre_material,
    i.precio_unitario
FROM obra_materiales om
INNER JOIN inventario i ON om.material_id = i.id
WHERE om.obra_id = ? AND om.tipo_material = 'inventario';

-- Consulta optimizada para resumen de recursos (usando índices)
SELECT 
    o.id AS obra_id,
    o.nombre AS obra_nombre,
    (SELECT COUNT(DISTINCT material_id) FROM obra_materiales WHERE obra_id = o.id) AS total_materiales,
    (SELECT COUNT(DISTINCT personal_id) FROM obra_personal WHERE obra_id = o.id AND activo = TRUE) AS total_personal
FROM obras o
WHERE o.id = ?;

-- Consulta optimizada para costo de materiales (separada)
SELECT 
    obra_id,
    SUM(
        CASE 
            WHEN tipo_material = 'vidrio' THEN 
                cantidad * (SELECT precio_m2 FROM vidrios WHERE id = material_id)
            WHEN tipo_material = 'inventario' THEN 
                cantidad * (SELECT precio_unitario FROM inventario WHERE id = material_id)
            ELSE 0
        END
    ) AS costo_total_materiales
FROM obra_materiales 
WHERE obra_id = ?
GROUP BY obra_id;

-- Consulta optimizada para costo de personal (separada)
SELECT 
    op.obra_id,
    SUM(
        CASE 
            WHEN op.fecha_fin IS NOT NULL THEN 
                DATEDIFF(op.fecha_fin, op.fecha_inicio) * p.costo_hora * 8
            WHEN op.activo = TRUE THEN 
                DATEDIFF(NOW(), op.fecha_inicio) * p.costo_hora * 8
            ELSE 0
        END
    ) AS costo_total_personal
FROM obra_personal op
INNER JOIN personal p ON op.personal_id = p.id
WHERE op.obra_id = ?
GROUP BY op.obra_id;

-- Consulta optimizada para verificar disponibilidad de materiales
-- Disponibilidad de vidrios
SELECT id, stock_disponible AS cantidad_disponible
FROM vidrios 
WHERE id = ?;

-- Disponibilidad de inventario
SELECT id, cantidad_disponible  
FROM inventario
WHERE id = ?;

-- Consulta optimizada para personal disponible
SELECT 
    p.id,
    p.nombre,
    p.apellido,
    p.especialidad,
    p.costo_hora,
    COALESCE(obras_activas.total, 0) AS obras_activas
FROM personal p
LEFT JOIN (
    SELECT personal_id, COUNT(*) AS total
    FROM obra_personal 
    WHERE activo = TRUE
    GROUP BY personal_id
) obras_activas ON p.id = obras_activas.personal_id
WHERE p.id = ? AND p.activo = TRUE;

-- Consulta para eficiencia de materiales (optimizada con índice)
SELECT 
    material_id,
    tipo_material,
    cantidad AS cantidad_asignada,
    cantidad_utilizada,
    CASE 
        WHEN cantidad > 0 THEN ROUND((cantidad_utilizada * 100.0 / cantidad), 2)
        ELSE 0 
    END AS porcentaje_utilizacion
FROM obra_materiales
WHERE obra_id = ?
ORDER BY porcentaje_utilizacion DESC;