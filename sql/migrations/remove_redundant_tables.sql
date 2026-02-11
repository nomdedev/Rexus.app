/*
 * MIGRACIÓN: ELIMINACIÓN DE TABLAS REDUNDANTES
 * Rexus.app - Auditoría de Base de Datos FASE 1.2
 *
 * Tablas a eliminar:
 * 1. inventario_items - redundante con inventario_perfiles
 * 2. reservas_stock - solapado con reservas_materiales
 *
 * Fecha: 2025-02-10
 * Prioridad: MEDIA
 * Precondición: Verificar que no hay dependencias activas
 */

USE [inventario];
GO

PRINT '';
PRINT '============================================';
PRINT 'MIGRACIÓN: TABLAS REDUNDANTES';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '============================================';
PRINT '';

-- ============================================
-- PASO 1: VERIFICAR DEPENDENCIAS
-- ============================================

PRINT 'PASO 1: Verificando dependencias...';
PRINT '';

-- Verificar foreign keys hacia inventario_items
IF EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE referenced_object_id = OBJECT_ID('inventario_items')
)
BEGIN
    PRINT '⚠️ ADVERTENCIA: inventario_items tiene foreign keys dependientes';
    PRINT '   Por favor revisar las siguientes dependencias:';

    SELECT
        OBJECT_NAME(fk.parent_object_id) AS tabla_dependiente,
        fk.name AS nombre_fk,
        COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS columna
    FROM sys.foreign_keys fk
    INNER JOIN sys.foreign_key_columns fkc
        ON fk.object_id = fkc.constraint_object_id
    WHERE fk.referenced_object_id = OBJECT_ID('inventario_items');
END
ELSE
BEGIN
    PRINT '✅ inventario_items no tiene foreign keys dependientes';
END
PRINT '';

-- Verificar foreign keys hacia reservas_stock
IF EXISTS (
    SELECT 1 FROM sys.foreign_keys
    WHERE referenced_object_id = OBJECT_ID('reservas_stock')
)
BEGIN
    PRINT '⚠️ ADVERTENCIA: reservas_stock tiene foreign keys dependientes';
    PRINT '   Por favor revisar las siguientes dependencias:';

    SELECT
        OBJECT_NAME(fk.parent_object_id) AS tabla_dependiente,
        fk.name AS nombre_fk,
        COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS columna
    FROM sys.foreign_keys fk
    INNER JOIN sys.foreign_key_columns fkc
        ON fk.object_id = fkc.constraint_object_id
    WHERE fk.referenced_object_id = OBJECT_ID('reservas_stock');
END
ELSE
BEGIN
    PRINT '✅ reservas_stock no tiene foreign keys dependientes';
END
PRINT '';

-- ============================================
-- PASO 2: VERIFICAR DATOS
-- ============================================

PRINT 'PASO 2: Verificando datos en tablas redundantes...';
PRINT '';

-- Verificar si inventario_items tiene datos
DECLARE @inventario_items_count INT;
SELECT @inventario_items_count = COUNT(*) FROM inventario_items WITH (NOLOCK);

IF @inventario_items_count > 0
BEGIN
    PRINT '⚠️ inventario_items contiene ' + CAST(@inventario_items_count AS VARCHAR) + ' registros';
    PRINT '   Se recomienda migrar los datos antes de eliminar';
    PRINT '';
    PRINT '   Script de migración sugerido:';
    PRINT '   INSERT INTO inventario_perfiles (...)';
    PRINT '   SELECT ... FROM inventario_items';
END
ELSE
BEGIN
    PRINT '✅ inventario_items está vacía (' + CAST(@inventario_items_count AS VARCHAR) + ' registros)';
END
PRINT '';

-- Verificar si reservas_stock tiene datos
DECLARE @reservas_stock_count INT;
SELECT @reservas_stock_count = COUNT(*) FROM reservas_stock WITH (NOLOCK);

IF @reservas_stock_count > 0
BEGIN
    PRINT '⚠️ reservas_stock contiene ' + CAST(@reservas_stock_count AS VARCHAR) + ' registros';
    PRINT '   Se recomienda migrar los datos a reservas_materiales';
    PRINT '';
    PRINT '   Script de migración sugerido:';
    PRINT '   INSERT INTO reservas_materiales (...)';
    PRINT '   SELECT ... FROM reservas_stock';
END
ELSE
BEGIN
    PRINT '✅ reservas_stock está vacía (' + CAST(@reservas_stock_count AS VARCHAR) + ' registros)';
END
PRINT '';

-- ============================================
-- PASO 3: MIGRACIÓN DE DATOS (si es necesario)
-- ============================================

-- Script de migración para inventario_items -> inventario_perfiles
-- DESCOMENTAR solo si hay datos que migrar

/*
IF @inventario_items_count > 0
BEGIN
    PRINT 'PASO 3a: Migrando datos de inventario_items...';

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Verificar columnas compatibles
        INSERT INTO inventario_perfiles (
            codigo, descripcion, tipo, categoria,
            stock_actual, stock_minimo, stock_maximo,
            precio_unitario, costo_unitario, activo
        )
        SELECT
            COALESCE(codigo, 'MIGRADO_' + CAST(id AS VARCHAR)),
            COALESCE(descripcion, 'Item migrado'),
            COALESCE(tipo, 'GENERAL'),
            COALESCE(categoria, 'VARIOS'),
            COALESCE(stock, 0),
            COALESCE(stock_minimo, 0),
            COALESCE(stock_maximo, 1000),
            COALESCE(precio, 0),
            COALESCE(costo, 0),
            1
        FROM inventario_items
        WHERE NOT EXISTS (
            SELECT 1 FROM inventario_perfiles
            WHERE inventario_perfiles.codigo = 'MIGRADO_' + CAST(inventario_items.id AS VARCHAR)
        );

        COMMIT TRANSACTION;
        PRINT '✅ Migración de inventario_items completada';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT '❌ Error en migración: ' + ERROR_MESSAGE();
    END CATCH
END
*/

-- Script de migración para reservas_stock -> reservas_materiales
-- DESCOMENTAR solo si hay datos que migrar

/*
IF @reservas_stock_count > 0
BEGIN
    PRINT 'PASO 3b: Migrando datos de reservas_stock...';

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT INTO reservas_materiales (
            producto_id, obra_id, cantidad,
            fecha_reserva, estado, creado_por
        )
        SELECT
            producto_id, obra_id, cantidad,
            fecha_reserva, estado, usuario_id
        FROM reservas_stock
        WHERE NOT EXISTS (
            SELECT 1 FROM reservas_materiales
            WHERE reservas_materiales.producto_id = reservas_stock.producto_id
              AND reservas_materiales.obra_id = reservas_stock.obra_id
        );

        COMMIT TRANSACTION;
        PRINT '✅ Migración de reservas_stock completada';
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        PRINT '❌ Error en migración: ' + ERROR_MESSAGE();
    END CATCH
END
*/

-- ============================================
-- PASO 4: ELIMINACIÓN DE TABLAS
-- ============================================

PRINT 'PASO 4: Eliminando tablas redundantes...';
PRINT '';

-- ELIMINAR inventario_items
-- DESCOMENTAR después de verificar que está vacío o migró los datos

/*
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'inventario_items')
BEGIN
    BEGIN TRY
        -- Eliminar constraints primero
        DECLARE @sql NVARCHAR(MAX) = N'';

        SELECT @sql = @sql + 'ALTER TABLE ' + OBJECT_SCHEMA_NAME(parent_object_id)
            + '.' + OBJECT_NAME(parent_object_id) + ' DROP CONSTRAINT ' + name + ';'
        FROM sys.foreign_keys
        WHERE referenced_object_id = OBJECT_ID('inventario_items');

        EXEC sp_executesql @sql;

        -- Eliminar la tabla
        DROP TABLE inventario_items;
        PRINT '✅ Tabla inventario_items eliminada';
    END TRY
    BEGIN CATCH
        PRINT '❌ Error al eliminar inventario_items: ' + ERROR_MESSAGE();
    END CATCH
END
ELSE
BEGIN
    PRINT 'ℹ️ Tabla inventario_items no existe';
END
*/

-- ELIMINAR reservas_stock
-- DESCOMENTAR después de verificar que está vacío o migró los datos

/*
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'reservas_stock')
BEGIN
    BEGIN TRY
        -- Eliminar constraints primero
        SET @sql = N'';

        SELECT @sql = @sql + 'ALTER TABLE ' + OBJECT_SCHEMA_NAME(parent_object_id)
            + '.' + OBJECT_NAME(parent_object_id) + ' DROP CONSTRAINT ' + name + ';'
        FROM sys.foreign_keys
        WHERE referenced_object_id = OBJECT_ID('reservas_stock');

        EXEC sp_executesql @sql;

        -- Eliminar la tabla
        DROP TABLE reservas_stock;
        PRINT '✅ Tabla reservas_stock eliminada';
    END TRY
    BEGIN CATCH
        PRINT '❌ Error al eliminar reservas_stock: ' + ERROR_MESSAGE();
    END CATCH
END
ELSE
BEGIN
    PRINT 'ℹ️ Tabla reservas_stock no existe';
END
*/

PRINT '';
PRINT '============================================';
PRINT '⚠️ ACCIÓN MANUAL REQUERIDA';
PRINT '============================================';
PRINT '';
PRINT 'Para completar esta migración:';
PRINT '1. Revisar las dependencias identificadas';
PRINT '2. Ejecutar los scripts de migración de datos (si aplica)';
PRINT '3. Descomentar y ejecutar la sección PASO 4';
PRINT '4. Verificar que las tablas fueron eliminadas';
PRINT '';
PRINT 'Comandos de verificación:';
PRINT '  SELECT * FROM information_schema.tables WHERE table_name = ''inventario_items''';
PRINT '  SELECT * FROM information_schema.tables WHERE table_name = ''reservas_stock''';
PRINT '';
