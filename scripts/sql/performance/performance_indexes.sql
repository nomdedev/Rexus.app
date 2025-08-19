USE inventario;
GO
CREATE NONCLUSTERED INDEX [idx_obras_activo_fecha]
ON [dbo].[obras] ([activo] ASC, [fecha_creacion] DESC)
WHERE [activo] = 1;
CREATE NONCLUSTERED INDEX [idx_obras_estado]
ON [dbo].[obras] ([estado] ASC)
INCLUDE ([id])
WHERE [activo] = 1;
CREATE NONCLUSTERED INDEX [idx_obras_codigo_activo]
ON [dbo].[obras] ([codigo_obra] ASC, [activo] ASC);
CREATE NONCLUSTERED INDEX [idx_obras_presupuesto]
ON [dbo].[obras] ([presupuesto_total] ASC)
WHERE [activo] = 1 AND [presupuesto_total] > 0;
CREATE NONCLUSTERED INDEX [idx_inventario_tipo]
ON [dbo].[inventario_perfiles] ([tipo] ASC)
WHERE [tipo] IS NOT NULL AND [tipo] != '';
CREATE NONCLUSTERED INDEX [idx_inventario_stock_critico]
ON [dbo].[inventario_perfiles] ([stock_actual] ASC, [stock_minimo] ASC)
INCLUDE ([id], [descripcion], [tipo])
WHERE [stock_actual] <= [stock_minimo];
CREATE NONCLUSTERED INDEX [idx_inventario_activo_fecha]
ON [dbo].[inventario_perfiles] ([activo] ASC, [fecha_actualizacion] DESC)
INCLUDE ([id], [descripcion], [tipo], [stock_actual])
WHERE [activo] = 1;
CREATE NONCLUSTERED INDEX [idx_inventario_descripcion]
ON [dbo].[inventario_perfiles] ([descripcion] ASC)
WHERE [activo] = 1;
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'compras')
BEGIN
    CREATE NONCLUSTERED INDEX [idx_compras_estado_fecha]
    ON [dbo].[compras] ([estado] ASC, [fecha_pedido] DESC)
    INCLUDE ([id], [total]);
    CREATE NONCLUSTERED INDEX [idx_compras_proveedor]
    ON [dbo].[compras] ([proveedor_id] ASC)
    INCLUDE ([fecha_pedido], [total], [estado]);
END
GO
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'detalles_obra')
BEGIN
    CREATE NONCLUSTERED INDEX [idx_detalles_obra_id]
    ON [dbo].[detalles_obra] ([obra_id] ASC)
    INCLUDE ([producto_id], [cantidad], [precio_unitario]);
END
GO
USE auditoria;
GO
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'auditoria')
BEGIN
    CREATE NONCLUSTERED INDEX [idx_auditoria_fecha_accion]
    ON [dbo].[auditoria] ([fecha] DESC, [accion] ASC)
    INCLUDE ([usuario_id], [tabla_afectada]);
    CREATE NONCLUSTERED INDEX [idx_auditoria_usuario]
    ON [dbo].[auditoria] ([usuario_id] ASC)
    INCLUDE ([fecha], [accion], [tabla_afectada]);
END
GO
USE users;
GO
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'usuarios')
BEGIN
    CREATE NONCLUSTERED INDEX [idx_usuarios_activo_rol]
    ON [dbo].[usuarios] ([activo] ASC, [rol] ASC)
    INCLUDE ([username], [ultimo_acceso]);
    CREATE NONCLUSTERED INDEX [idx_usuarios_ultimo_acceso]
    ON [dbo].[usuarios] ([ultimo_acceso] DESC)
    WHERE [activo] = 1;
END
GO
USE inventario;
GO
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'obras')
BEGIN
    UPDATE STATISTICS [dbo].[obras] WITH FULLSCAN;
END
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'inventario_perfiles')
BEGIN
    UPDATE STATISTICS [dbo].[inventario_perfiles] WITH FULLSCAN;
END
PRINT '=====================================================================';
PRINT 'VERIFICACIÓN DE ÍNDICES DE RENDIMIENTO';
PRINT '=====================================================================';
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