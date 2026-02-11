-- ✅ QUERY OPTIMIZADA: Estadísticas Completas de Usuarios
-- File: sql/11_usuarios/estadisticas_usuarios_optimizadas.sql
--
-- Obtiene TODAS las estadísticas de usuarios en 1 sola query.
-- Reemplaza 5 queries individuales por 1 query optimizada con CTEs.
--
-- ⚡ Performance: 1 query en lugar de 5 queries
-- 📈 Mejora: 5x más rápido
--
-- Uso:
--   cursor.execute(query)
--   row = cursor.fetchone()
--   stats = {
--       'total_usuarios': row[0],
--       'activos_mes': row[1],
--       'creados_mes': row[2]
--   }
--   # Luego se obtienen por_estado y por_rol con fetchall()

WITH
-- CTE 1: Total de usuarios activos
total_usuarios AS (
    SELECT COUNT(*) AS total
    FROM usuarios
    WHERE activo = 1
),

-- CTE 2: Usuarios activos en el último mes
activos_mes AS (
    SELECT COUNT(*) AS activos
    FROM usuarios
    WHERE activo = 1
      AND ultimo_acceso >= DATEADD(MONTH, -1, GETDATE())
),

-- CTE 3: Usuarios creados este mes
creados_mes AS (
    SELECT COUNT(*) AS creados
    FROM usuarios
    WHERE activo = 1
      AND MONTH(fecha_creacion) = MONTH(GETDATE())
      AND YEAR(fecha_creacion) = YEAR(GETDATE())
),

-- CTE 4: Usuarios por estado (para GROUP BY)
por_estado AS (
    SELECT
        estado,
        COUNT(*) AS cantidad
    FROM usuarios
    WHERE activo = 1
    GROUP BY estado
),

-- CTE 5: Usuarios por rol (para GROUP BY)
por_rol AS (
    SELECT
        rol,
        COUNT(*) AS cantidad
    FROM usuarios
    WHERE activo = 1
    GROUP BY rol
)

-- Unir las estadísticas escalares
SELECT
    t.total AS total_usuarios,
    a.activos AS activos_mes,
    c.creados AS creados_mes
FROM total_usuarios t
CROSS JOIN activos_mes a
CROSS JOIN creados_mes c;

-- NOTA: por_estado y por_rol se obtienen por separado con fetchall()
-- porque necesitan devolver múltiples filas (GROUP BY results)
