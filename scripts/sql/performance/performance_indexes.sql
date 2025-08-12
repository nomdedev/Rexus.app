-- =====================================================================
-- ÍNDICES DE RENDIMIENTO PARA REXUS.APP
-- Mejoran el rendimiento de consultas críticas identificadas
-- =====================================================================

-- Usar la base de datos inventario para datos de negocio
USE inventario;
GO

-- =====================================================================
-- ÍNDICES PARA TABLA OBRAS
-- =====================================================================

-- Optimiza obtener_todas_obras con filtro activo y ordenamiento por fecha
CREATE NONCLUSTERED INDEX [idx_obras_activo_fecha]
ON [dbo].[obras] ([activo] ASC, [fecha_creacion] DESC)
WHERE [activo] = 1;

-- Optimiza estadísticas por estado
CREATE NONCLUSTERED INDEX [idx_obras_estado]
ON [dbo].[obras] ([estado] ASC)
INCLUDE ([id])
WHERE [activo] = 1;

-- Optimiza búsqueda y validación por código de obra
CREATE NONCLUSTERED INDEX [idx_obras_codigo_activo]
ON [dbo].[obras] ([codigo_obra] ASC, [activo] ASC);

-- Optimiza consultas de presupuesto para estadísticas
CREATE NONCLUSTERED INDEX [idx_obras_presupuesto]
ON [dbo].[obras] ([presupuesto_total] ASC)
WHERE [activo] = 1 AND [presupuesto_total] > 0;

-- =====================================================================
-- ÍNDICES PARA TABLA INVENTARIO_PERFILES
-- =====================================================================

-- Optimiza obtener_categorias - consulta DISTINCT por tipo
CREATE NONCLUSTERED INDEX [idx_inventario_tipo]
ON [dbo].[inventario_perfiles] ([tipo] ASC)
WHERE [tipo] IS NOT NULL AND [tipo] != '';

-- Optimiza consultas de stock bajo crítico
CREATE NONCLUSTERED INDEX [idx_inventario_stock_critico]
ON [dbo].[inventario_perfiles] ([stock_actual] ASC, [stock_minimo] ASC)
INCLUDE ([id], [descripcion], [tipo])
WHERE [stock_actual] <= [stock_minimo];

-- Optimiza listados paginados de productos activos
CREATE NONCLUSTERED INDEX [idx_inventario_activo_fecha]
ON [dbo].[inventario_perfiles] ([activo] ASC, [fecha_actualizacion] DESC)
INCLUDE ([id], [descripcion], [tipo], [stock_actual])
WHERE [activo] = 1;

-- Optimiza búsquedas por descripción/nombre de producto
CREATE NONCLUSTERED INDEX [idx_inventario_descripcion]
ON [dbo].[inventario_perfiles] ([descripcion] ASC)
WHERE [activo] = 1;

-- =====================================================================
-- ÍNDICES PARA TABLA COMPRAS (si existe)
-- =====================================================================

-- Optimiza filtros por estado y fecha de pedido
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'compras')
BEGIN
    CREATE NONCLUSTERED INDEX [idx_compras_estado_fecha]
    ON [dbo].[compras] ([estado] ASC, [fecha_pedido] DESC)
    INCLUDE ([id], [total]);

    -- Optimiza consultas por proveedor
    CREATE NONCLUSTERED INDEX [idx_compras_proveedor]
    ON [dbo].[compras] ([proveedor_id] ASC)
    INCLUDE ([fecha_pedido], [total], [estado]);
END
GO

-- =====================================================================
-- ÍNDICES PARA TABLA DETALLES_OBRA (si existe)
-- =====================================================================

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'detalles_obra')
BEGIN
    -- Optimiza consultas de detalles por obra (N+1 prevention)
    CREATE NONCLUSTERED INDEX [idx_detalles_obra_id]
    ON [dbo].[detalles_obra] ([obra_id] ASC)
    INCLUDE ([producto_id], [cantidad], [precio_unitario]);
END
GO

-- =====================================================================
-- ÍNDICES PARA AUDITORÍA (base auditoria)
-- =====================================================================

USE auditoria;
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'auditoria')
BEGIN
    -- Optimiza consultas de auditoría por fecha (más frecuente)
    CREATE NONCLUSTERED INDEX [idx_auditoria_fecha_accion]
    ON [dbo].[auditoria] ([fecha] DESC, [accion] ASC)
    INCLUDE ([usuario_id], [tabla_afectada]);

    -- Optimiza consultas de auditoría por usuario
    CREATE NONCLUSTERED INDEX [idx_auditoria_usuario]
    ON [dbo].[auditoria] ([usuario_id] ASC)
    INCLUDE ([fecha], [accion], [tabla_afectada]);
END
GO

-- =====================================================================
-- ÍNDICES PARA USUARIOS (base users)
-- =====================================================================

USE users;
GO

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
BEGIN
    -- Optimiza consultas de usuarios activos por rol
    CREATE NONCLUSTERED INDEX [idx_usuarios_activo_rol]
    ON [dbo].[usuarios] ([activo] ASC, [rol] ASC)
    INCLUDE ([username], [ultimo_acceso]);

    -- Optimiza estadísticas de actividad de usuarios
    CREATE NONCLUSTERED INDEX [idx_usuarios_ultimo_acceso]
    ON [dbo].[usuarios] ([ultimo_acceso] DESC)
    WHERE [activo] = 1;
END
GO

-- =====================================================================
-- ESTADÍSTICAS ADICIONALES
-- =====================================================================

-- Volver a base inventario para estadísticas
USE inventario;
GO

-- Actualizar estadísticas existentes para mejor optimización
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'obras')
BEGIN
    UPDATE STATISTICS [dbo].[obras] WITH FULLSCAN;
END

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'inventario_perfiles')
BEGIN
    UPDATE STATISTICS [dbo].[inventario_perfiles] WITH FULLSCAN;
END

-- =====================================================================
-- VERIFICACIÓN DE ÍNDICES CREADOS
-- =====================================================================

PRINT '=====================================================================';
PRINT 'VERIFICACIÓN DE ÍNDICES DE RENDIMIENTO';
PRINT '=====================================================================';

-- Mostrar índices creados para obras
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'obras')
BEGIN
    PRINT 'Índices en tabla OBRAS:';
    SELECT 
        i.name AS index_name,
        CASE WHEN i.is_unique = 1 THEN 'UNIQUE' ELSE 'NON-UNIQUE' END AS index_type,
        ds.name AS filegroup_name
    FROM sys.indexes i
    INNER JOIN sys.data_spaces ds ON i.data_space_id = ds.data_space_id
    WHERE i.object_id = OBJECT_ID('dbo.obras')
    AND i.name LIKE 'idx_obras_%';
END

-- Mostrar índices creados para inventario_perfiles
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'inventario_perfiles')
BEGIN
    PRINT '';
    PRINT 'Índices en tabla INVENTARIO_PERFILES:';
    SELECT 
        i.name AS index_name,
        CASE WHEN i.is_unique = 1 THEN 'UNIQUE' ELSE 'NON-UNIQUE' END AS index_type,
        ds.name AS filegroup_name
    FROM sys.indexes i
    INNER JOIN sys.data_spaces ds ON i.data_space_id = ds.data_space_id
    WHERE i.object_id = OBJECT_ID('dbo.inventario_perfiles')
    AND i.name LIKE 'idx_inventario_%';
END

PRINT '';
PRINT 'Índices de rendimiento aplicados exitosamente.';
PRINT 'Las consultas optimizadas deberían mostrar mejoras de rendimiento.';
PRINT '=====================================================================';

GO