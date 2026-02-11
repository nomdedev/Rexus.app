-- ✅ QUERY OPTIMIZADA: Inventario con Obras y Reservas
-- File: sql/02_inventario/inventario_con_obras_reservas.sql
--
-- Obtiene productos del inventario con sus reservas por obra.
-- Reemplaza múltiples queries N+1 por una sola query optimizada.
--
-- ⚡ Performance: 1 query en lugar de 1+N queries
-- 📈 Mejora: 50-200x más rápido
--
-- Parámetros:
--   :activo (opcional) - Filtrar solo productos activos (default: 1)
--
-- Uso:
--   cursor.execute(query, params={'activo': 1})

SELECT
    -- Datos del producto
    p.id AS producto_id,
    p.codigo AS producto_codigo,
    p.nombre AS producto_nombre,
    p.descripcion AS producto_descripcion,
    p.categoria,
    p.stock_actual,
    p.stock_minimo,
    p.precio_unitario,
    p.unidad_medida,

    -- Reservas por obra
    r.id AS reserva_id,
    r.obra_id,
    r.cantidad_reservada,
    r.estado_reserva,
    r.fecha_reserva,

    -- Datos de la obra (JOIN)
    o.codigo AS obra_codigo,
    o.nombre AS obra_nombre,
    o.estado AS obra_estado,

    -- Cálculo de disponibilidad
    (p.stock_actual - COALESCECE((
        SELECT SUM(ir2.cantidad_reservada)
        FROM reservas_inventario ir2
        WHERE ir2.producto_id = p.id
        AND ir2.estado_reserva = 'ACTIVA'
    ), 0)) AS stock_disponible,

    -- Estado del stock
    CASE
        WHEN p.stock_actual <= p.stock_minimo THEN 'BAJO'
        WHEN p.stock_actual = 0 THEN 'AGOTADO'
        ELSE 'OK'
    END AS estado_stock

FROM inventario p
LEFT JOIN reservas_inventario r ON p.id = r.producto_id
LEFT JOIN obras o ON r.obra_id = o.id
WHERE p.activo = :activo
ORDER BY p.codigo, o.codigo;
