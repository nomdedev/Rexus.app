/*
 * MIGRACIÓN: ESTANDARIZACIÓN DE NOMBRES DE COLUMNAS
 * Rexus.app - Auditoría de Base de Datos FASE 1.2
 *
 * Corrige inconsistencias en nombres de columnas para mantener
 * consistencia en toda la base de datos.
 *
 * Reglas de estandarización:
 * - id_usuario: Para IDs de usuarios externos
 * - ultimo_login: Para última conexión
 * - fecha_hora: Para timestamps completos
 * - stock_actual: Para stock actual
 * - id_perfil: Para IDs de perfiles de inventario
 *
 * Fecha: 2025-02-10
 * Prioridad: MEDIA
 */

USE [users];
GO

PRINT '';
PRINT '============================================';
PRINT 'ESTANDARIZACIÓN DE COLUMNAS - BD USERS';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '============================================';
PRINT '';

-- ============================================
-- BASE DE DATOS: USERS
-- ============================================

-- 1. usuarios: ultima_conexion -> ultimo_login
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('usuarios')
      AND name = 'ultima_conexion'
)
BEGIN
    PRINT '✅ Renombrando ultima_conexion a ultimo_login en tabla usuarios';

    -- Verificar si ya existe ultimo_login
    IF NOT EXISTS (
        SELECT 1 FROM sys.columns
        WHERE object_id = OBJECT_ID('usuarios')
          AND name = 'ultimo_login'
    )
    BEGIN
        EXEC sp_rename 'usuarios.ultima_conexion', 'ultimo_login', 'COLUMN';
        PRINT '   Columna renombrada exitosamente';
    END
    ELSE
    BEGIN
        PRINT '   ⚠️ ultimo_login ya existe, migrando datos...';

        -- Migrar datos y eliminar columna antigua
        DECLARE @sql NVARCHAR(MAX);

        -- Si ultima_conexion tiene datos y ultimo_login está vacío
        SET @sql = N'
        UPDATE u
        SET ultimo_login = COALESCE(u.ultimo_login, u.ultima_conexion)
        FROM usuarios u
        WHERE u.ultima_conexion IS NOT NULL;';

        EXEC sp_executesql @sql;

        -- Eliminar columna antigua
        SET @sql = N'ALTER TABLE usuarios DROP COLUMN ultima_conexion;';
        EXEC sp_executesql @sql;

        PRINT '   Datos migrados y columna antigua eliminada';
    END
END
ELSE
BEGIN
    PRINT 'ℹ️ Columna ultima_conexion no encontrada en usuarios';
END
PRINT '';

-- 2. permisos_modulos: usuario_id -> id_usuario
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('permisos_modulos')
      AND name = 'usuario_id'
)
BEGIN
    PRINT '✅ Renombrando usuario_id a id_usuario en tabla permisos_modulos';

    IF NOT EXISTS (
        SELECT 1 FROM sys.columns
        WHERE object_id = OBJECT_ID('permisos_modulos')
          AND name = 'id_usuario'
    )
    BEGIN
        EXEC sp_rename 'permisos_modulos.usuario_id', 'id_usuario', 'COLUMN';
        PRINT '   Columna renombrada exitosamente';
    END
    ELSE
    BEGIN
        -- Ambas existen, hay que consolidar
        PRINT '   ⚠️ Ambas columnas existen, consolidando...';

        -- Crear columna temporal si es necesario
        -- (lógica de migración específica según datos)

        PRINT '   ⚠️ Requiere migración manual - revisar datos';
    END
END
ELSE
BEGIN
    PRINT 'ℹ️ Columna usuario_id no encontrada en permisos_modulos';
END
PRINT '';

-- 3. logs_usuarios: fecha -> fecha_hora
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('logs_usuarios')
      AND name = 'fecha'
)
BEGIN
    PRINT '✅ Renombrando fecha a fecha_hora en tabla logs_usuarios';

    IF NOT EXISTS (
        SELECT 1 FROM sys.columns
        WHERE object_id = OBJECT_ID('logs_usuarios')
          AND name = 'fecha_hora'
    )
    BEGIN
        EXEC sp_rename 'logs_usuarios.fecha', 'fecha_hora', 'COLUMN';
        PRINT '   Columna renombrada exitosamente';
    END
END
ELSE
BEGIN
    PRINT 'ℹ️ Columna fecha no encontrada en logs_usuarios';
END
PRINT '';

GO

USE [inventario];
GO

PRINT '';
PRINT '============================================';
PRINT 'ESTANDARIZACIÓN DE COLUMNAS - BD INVENTARIO';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '============================================';
PRINT '';

-- ============================================
-- BASE DE DATOS: INVENTARIO
-- ============================================

-- 4. inventario_perfiles: stock -> stock_actual
IF EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID('inventario_perfiles')
      AND name = 'stock'
)
BEGIN
    PRINT '✅ Renombrando stock a stock_actual en tabla inventario_perfiles';

    IF NOT EXISTS (
        SELECT 1 FROM sys.columns
        WHERE object_id = OBJECT_ID('inventario_perfiles')
          AND name = 'stock_actual'
    )
    BEGIN
        EXEC sp_rename 'inventario_perfiles.stock', 'stock_actual', 'COLUMN';
        PRINT '   Columna renombrada exitosamente';
    END
    ELSE
    BEGIN
        PRINT '   ⚠️ stock_actual ya existe, eliminando stock...';

        -- Verificar si hay datos diferentes
        DECLARE @check_sql NVARCHAR(MAX);
        DECLARE @has_different_data BIT = 0;

        SET @check_sql = N'
        SELECT @has_different_data = CASE
            WHEN EXISTS (
                SELECT 1 FROM inventario_perfiles
                WHERE stock IS NOT NULL
                  AND stock_actual IS NOT NULL
                  AND stock <> stock_actual
            ) THEN 1
            ELSE 0
        END;';

        EXEC sp_executesql @check_sql, N'@has_different_data BIT OUTPUT', @has_different_data OUTPUT;

        IF @has_different_data = 1
        BEGIN
            PRINT '   ⚠️ Hay datos diferentes entre stock y stock_actual';
            PRINT '   Se requiere revisión manual antes de eliminar';
        END
        ELSE
        BEGIN
            -- Migrar datos si stock_actual está NULL
            SET @check_sql = N'
            UPDATE inventario_perfiles
            SET stock_actual = stock
            WHERE stock_actual IS NULL AND stock IS NOT NULL;';

            EXEC sp_executesql @check_sql;
            PRINT '   Datos migrados de stock a stock_actual';

            -- Eliminar columna antigua
            SET @check_sql = N'ALTER TABLE inventario_perfiles DROP COLUMN stock;';
            EXEC sp_executesql @check_sql;
            PRINT '   Columna stock eliminada';
        END
    END
END
ELSE
BEGIN
    PRINT 'ℹ️ Columna stock no encontrada en inventario_perfiles';
END
PRINT '';

-- 5. Estandarizar id_item -> id_perfil en tablas relacionadas
PRINT '✅ Verificando columnas id_item que deben ser id_perfil...';

-- Lista de tablas donde verificar
DECLARE tables_cursor CURSOR FOR
    t.name AS table_name
FROM sys.tables t
INNER JOIN sys.columns c ON t.object_id = c.object_id
WHERE c.name = 'id_item'
  AND t.is_ms_shipped = 0
ORDER BY t.name;

DECLARE @table_name NVARCHAR(128);
DECLARE @alter_sql NVARCHAR(MAX);

OPEN tables_cursor;
FETCH NEXT FROM tables_cursor INTO @table_name;

WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT '   Encontrado id_item en: ' + @table_name;

    -- Verificar si id_perfil ya existe
    IF NOT EXISTS (
        SELECT 1 FROM sys.columns
        WHERE object_id = OBJECT_ID(@table_name)
          AND name = 'id_perfil'
    )
    BEGIN
        SET @alter_sql = 'EXEC sp_rename ''' + @table_name + '.id_item'', ''id_perfil'', ''COLUMN''';
        PRINT '   → Renombrando a id_perfil';

        BEGIN TRY
            EXEC sp_executesql @alter_sql;
            PRINT '   ✅ Renombrado exitosamente';
        END TRY
        BEGIN CATCH
            PRINT '   ⚠️ Error: ' + ERROR_MESSAGE();
        END CATCH
    END
    ELSE
    BEGIN
        PRINT '   → id_perfil ya existe, requiere consolidación manual';
    END

    FETCH NEXT FROM tables_cursor INTO @table_name;
END

CLOSE tables_cursor;
DEALLOCATE tables_cursor;
PRINT '';

GO

-- ============================================
-- VERIFICACIÓN FINAL
-- ============================================

PRINT '';
PRINT '============================================';
PRINT 'VERIFICACIÓN FINAL';
PRINT '============================================';
PRINT '';

USE [users];
PRINT 'Base de datos [users]:';
PRINT '  - Columnas en usuarios:ultima_conexion: ' +
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'ultima_conexion')
        THEN '❌ AÚN EXISTE (debe eliminarse)' ELSE '✅ Eliminada' END;
PRINT '  - Columnas en usuarios:ultimo_login: ' +
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('usuarios') AND name = 'ultimo_login')
        THEN '✅ Existe' ELSE '❌ NO existe (debe crearse)' END;
PRINT '';

USE [inventario];
PRINT 'Base de datos [inventario]:';
PRINT '  - Columnas en inventario_perfiles:stock: ' +
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('inventario_perfiles') AND name = 'stock')
        THEN '❌ AÚN EXISTE (debe eliminarse)' ELSE '✅ Eliminada' END;
PRINT '  - Columnas en inventario_perfiles:stock_actual: ' +
    CASE WHEN EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('inventario_perfiles') AND name = 'stock_actual')
        THEN '✅ Existe' ELSE '❌ NO existe (debe crearse)' END;
PRINT '';

-- Contar columnas id_item restantes
DECLARE @id_item_count INT;
SELECT @id_item_count = COUNT(*)
FROM sys.columns c
INNER JOIN sys.tables t ON c.object_id = t.object_id
WHERE c.name = 'id_item'
  AND t.is_ms_shipped = 0;

PRINT '  - Columnas id_item restantes: ' + CAST(@id_item_count AS VARCHAR);
IF @id_item_count = 0
    PRINT '    ✅ Todas estandarizadas a id_perfil';
ELSE
    PRINT '    ⚠️ Requieren revisión manual';

PRINT '';
PRINT '============================================';
PRINT '✅ ESTANDARIZACIÓN COMPLETADA';
PRINT '============================================';
PRINT '';
