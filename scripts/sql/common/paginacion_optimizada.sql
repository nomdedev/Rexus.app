SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY fecha_creacion DESC) as row_num
    FROM {tabla}
    WHERE activo = 1
) t
WHERE row_num > @offset AND row_num <= (@offset + @limit);
SELECT * FROM {tabla}
WHERE activo = 1
ORDER BY fecha_creacion DESC
LIMIT ? OFFSET ?;
SELECT COUNT(*) as total
FROM {tabla}
WHERE activo = 1;
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
SELECT COUNT(*) as total
FROM {tabla}
WHERE activo = 1
  AND (
    nombre LIKE ? OR
    descripcion LIKE ? OR
    codigo LIKE ?
  );
SELECT * FROM {tabla}
WHERE activo = 1
  AND (@estado IS NULL OR estado = @estado)
  AND (@fecha_desde IS NULL OR fecha_creacion >= @fecha_desde)
  AND (@fecha_hasta IS NULL OR fecha_creacion <= @fecha_hasta)
ORDER BY fecha_creacion DESC
OFFSET @offset ROWS FETCH NEXT @limit ROWS ONLY;
SELECT * FROM {tabla}
WHERE activo = 1
ORDER BY id
LIMIT ?;
SELECT * FROM {tabla}
WHERE activo = 1 AND id > ?
ORDER BY id
LIMIT ?;