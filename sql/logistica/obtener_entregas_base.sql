-- scripts/sql/logistica/obtener_entregas_base.sql
-- Consulta base para obtener entregas con información completa
-- Sin parámetros base, pero se aplican filtros dinámicamente

SELECT 
    e.id,
    e.id as numero_entrega,  -- Usar ID como número de entrega si la columna no existe
    e.fecha_entrega,
    e.estado,
    e.obra_id,
    e.transporte_id,
    e.observaciones,
    ISNULL(o.id, 0) as obra_nombre,  -- Usar ID si no hay columna nombre
    e.direccion_entrega as obra_direccion,
    ISNULL(t.id, 0) as transporte_nombre,  -- Usar ID si no hay columna nombre
    'TRANSPORTE' as transporte_tipo  -- Valor por defecto
FROM [entregas] e
LEFT JOIN [obras] o ON e.obra_id = o.id
LEFT JOIN [transportes] t ON e.transporte_id = t.id
WHERE 1=1
