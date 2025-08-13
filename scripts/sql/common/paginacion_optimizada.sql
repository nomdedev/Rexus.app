-- Consultas SQL optimizadas para paginación eficiente
-- Soporte para OFFSET/LIMIT con conteo optimizado

-- === PAGINACIÓN BÁSICA ===

-- Obtener registros paginados (SQL Server/PostgreSQL)
-- Parámetros: @offset, @limit
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY fecha_creacion DESC) as row_num
    FROM {tabla}
    WHERE activo = 1
) t
WHERE row_num > @offset AND row_num <= (@offset + @limit);

-- Obtener registros paginados (MySQL/SQLite compatible)
-- Parámetros: offset, limit
SELECT * FROM {tabla}
WHERE activo = 1
ORDER BY fecha_creacion DESC
LIMIT ? OFFSET ?;

-- === CONTEO EFICIENTE ===

-- Contar total de registros (optimizado)
SELECT COUNT(*) as total
FROM {tabla}
WHERE activo = 1;

-- === PAGINACIÓN CON BÚSQUEDA ===

-- Búsqueda paginada optimizada
-- Parámetros: search_term, offset, limit
SELECT * FROM {tabla}
WHERE activo = 1
  AND (
    nombre LIKE ? OR
    descripcion LIKE ? OR
    codigo LIKE ?
  )
ORDER BY 
  CASE 
    WHEN nombre LIKE ? THEN 1
    WHEN codigo LIKE ? THEN 2
    ELSE 3
  END,
  fecha_creacion DESC
LIMIT ? OFFSET ?;

-- Conteo de búsqueda
SELECT COUNT(*) as total
FROM {tabla}
WHERE activo = 1
  AND (
    nombre LIKE ? OR
    descripcion LIKE ? OR
    codigo LIKE ?
  );

-- === PAGINACIÓN CON FILTROS ===

-- Paginación con filtros múltiples
-- Parámetros: estado, fecha_desde, fecha_hasta, offset, limit
SELECT * FROM {tabla}
WHERE activo = 1
  AND (@estado IS NULL OR estado = @estado)
  AND (@fecha_desde IS NULL OR fecha_creacion >= @fecha_desde)
  AND (@fecha_hasta IS NULL OR fecha_creacion <= @fecha_hasta)
ORDER BY fecha_creacion DESC
OFFSET @offset ROWS FETCH NEXT @limit ROWS ONLY;

-- === OPTIMIZACIONES DE RENDIMIENTO ===

-- Índices recomendados para paginación eficiente
-- CREATE INDEX idx_tabla_activo_fecha ON {tabla} (activo, fecha_creacion DESC);
-- CREATE INDEX idx_tabla_busqueda ON {tabla} (activo, nombre, codigo, descripcion);
-- CREATE INDEX idx_tabla_filtros ON {tabla} (activo, estado, fecha_creacion);

-- === PAGINACIÓN CON CURSOR (para tablas muy grandes) ===

-- Primera página (cursor-based)
SELECT * FROM {tabla}
WHERE activo = 1
ORDER BY id
LIMIT ?;

-- Páginas siguientes (cursor-based)
-- Parámetro: last_id del registro anterior
SELECT * FROM {tabla}
WHERE activo = 1 AND id > ?
ORDER BY id
LIMIT ?;