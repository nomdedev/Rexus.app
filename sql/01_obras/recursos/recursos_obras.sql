INSERT INTO obra_materiales (
    obra_id,
    material_id,
    tipo_material,
    cantidad,
    cantidad_utilizada,
    fecha_asignacion,
    created_at,
    updated_at
) VALUES (?, ?, ?, ?, 0, GETDATE(), GETDATE(), GETDATE());
SELECT
    om.id,
    om.obra_id,
    om.material_id,
    om.tipo_material,
    om.cantidad,
    om.cantidad_utilizada,
    om.fecha_asignacion,
    CASE
        WHEN om.tipo_material = 'vidrio' THEN v.tipo
        WHEN om.tipo_material = 'inventario' THEN i.nombre
        ELSE om.tipo_material
    END AS nombre_material,
    CASE
        WHEN om.tipo_material = 'vidrio' THEN v.precio_m2
        WHEN om.tipo_material = 'inventario' THEN i.precio_unitario
        ELSE 0
    END AS precio_unitario
FROM obra_materiales om
LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
LEFT JOIN inventario i ON om.material_id = i.id AND om.tipo_material = 'inventario'
WHERE om.obra_id = ?;
UPDATE obra_materiales
SET
    cantidad = cantidad - ?,
    updated_at = GETDATE()
WHERE obra_id = ? AND material_id = ? AND cantidad >= ?;
DELETE FROM obra_materiales
WHERE obra_id = ? AND material_id = ? AND cantidad <= 0;
INSERT INTO obra_personal (
    obra_id,
    personal_id,
    rol,
    fecha_inicio,
    fecha_fin,
    activo,
    created_at,
    updated_at
) VALUES (?, ?, ?, ?, NULL, 1, GETDATE(), GETDATE());
SELECT
    op.id,
    op.obra_id,
    op.personal_id,
    op.rol,
    op.fecha_inicio,
    op.fecha_fin,
    op.activo,
    p.nombre,
    p.apellido,
    p.especialidad,
    p.costo_hora
FROM obra_personal op
LEFT JOIN personal p ON op.personal_id = p.id
WHERE op.obra_id = ? AND op.activo = TRUE;
UPDATE obra_personal
SET
    activo = FALSE,
    fecha_fin = GETDATE(),
    updated_at = GETDATE()
WHERE obra_id = ? AND personal_id = ?;
SELECT
    o.id AS obra_id,
    o.nombre AS obra_nombre,
    COUNT(DISTINCT om.material_id) AS total_materiales,
    COUNT(DISTINCT op.personal_id) AS total_personal,
    SUM(
        CASE
            WHEN om.tipo_material = 'vidrio' THEN om.cantidad * v.precio_m2
            WHEN om.tipo_material = 'inventario' THEN om.cantidad * i.precio_unitario
            ELSE 0
        END
    ) AS costo_materiales,
    SUM(
        CASE
            WHEN op.activo = TRUE THEN
                COALESCE(p.costo_hora * 8, 0)
            ELSE 0
        END
    ) AS costo_personal_diario
FROM obras o
LEFT JOIN obra_materiales om ON o.id = om.obra_id
LEFT JOIN obra_personal op ON o.id = op.obra_id
LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
LEFT JOIN inventario i ON om.material_id = i.id AND om.tipo_material = 'inventario'
LEFT JOIN personal p ON op.personal_id = p.id
WHERE o.id = ?
GROUP BY o.id, o.nombre;
SELECT
    o.id,
    o.nombre,
    o.presupuesto,
    COALESCE(costos_materiales.total_materiales, 0) AS costo_materiales,
    COALESCE(costos_personal.total_personal, 0) AS costo_personal,
    (COALESCE(costos_materiales.total_materiales, 0) +
     COALESCE(costos_personal.total_personal, 0)) AS costo_total_calculado
FROM obras o
LEFT JOIN (
    SELECT
        om.obra_id,
        SUM(
            CASE
                WHEN om.tipo_material = 'vidrio' THEN om.cantidad * v.precio_m2
                WHEN om.tipo_material = 'inventario' THEN om.cantidad * i.precio_unitario
                ELSE 0
            END
        ) AS total_materiales
    FROM obra_materiales om
    LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
    LEFT JOIN inventario i ON om.material_id = i.id AND om.tipo_material = 'inventario'
    GROUP BY om.obra_id
) costos_materiales ON o.id = costos_materiales.obra_id
LEFT JOIN (
    SELECT
        op.obra_id,
        SUM(
            CASE
                WHEN op.fecha_fin IS NOT NULL THEN
                    DATEDIFF(op.fecha_fin, op.fecha_inicio) * p.costo_hora * 8
                WHEN op.activo = TRUE THEN
                    DATEDIFF(day, op.fecha_inicio, GETDATE()) * p.costo_hora * 8
                ELSE 0
            END
        ) AS total_personal
    FROM obra_personal op
    LEFT JOIN personal p ON op.personal_id = p.id
    GROUP BY op.obra_id
) costos_personal ON o.id = costos_personal.obra_id
WHERE o.id = ?;
SELECT
    id,
    CASE
        WHEN ? = 'vidrio' THEN
            (SELECT stock_disponible FROM vidrios WHERE id = ?)
        WHEN ? = 'inventario' THEN
            (SELECT cantidad_disponible FROM inventario WHERE id = ?)
        ELSE 0
    END AS cantidad_disponible;
SELECT
    p.id,
    p.nombre,
    p.apellido,
    p.especialidad,
    COUNT(op.id) AS obras_activas
FROM personal p
LEFT JOIN obra_personal op ON p.id = op.personal_id AND op.activo = TRUE
WHERE p.id = ? AND p.activo = TRUE
GROUP BY p.id, p.nombre, p.apellido, p.especialidad;
UPDATE obra_materiales
SET
    cantidad_utilizada = cantidad_utilizada + ?,
    updated_at = GETDATE()
WHERE obra_id = ? AND material_id = ?;
SELECT
    om.id,
    om.obra_id,
    om.material_id,
    om.tipo_material,
    om.cantidad,
    om.cantidad_utilizada,
    om.fecha_asignacion,
    o.nombre AS obra_nombre,
    CASE
        WHEN om.tipo_material = 'vidrio' THEN v.tipo
        WHEN om.tipo_material = 'inventario' THEN i.nombre
        ELSE om.tipo_material
    END AS nombre_material
FROM obra_materiales om
LEFT JOIN obras o ON om.obra_id = o.id
LEFT JOIN vidrios v ON om.material_id = v.id AND om.tipo_material = 'vidrio'
LEFT JOIN inventario i ON om.material_id = i.id AND om.tipo_material = 'inventario'
WHERE om.material_id = ? AND om.tipo_material = ?
ORDER BY om.fecha_asignacion DESC;
SELECT
    om.obra_id,
    o.nombre AS obra_nombre,
    om.material_id,
    om.tipo_material,
    om.cantidad AS cantidad_asignada,
    om.cantidad_utilizada,
    CASE
        WHEN om.cantidad > 0 THEN
            (om.cantidad_utilizada * 100.0 / om.cantidad)
        ELSE 0
    END AS porcentaje_utilizacion
FROM obra_materiales om
LEFT JOIN obras o ON om.obra_id = o.id
WHERE om.obra_id = ?
ORDER BY porcentaje_utilizacion DESC;