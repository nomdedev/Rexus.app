-- Índices de Performance para Rexus.app
-- Creación de índices críticos para optimizar consultas frecuentes
-- Fecha: Agosto 2025

-- ============================================================================
-- ÍNDICES CRÍTICOS FALTANTES IDENTIFICADOS EN AUDITORÍA
-- ============================================================================

-- Inventario: código de producto (búsquedas frecuentes)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_inventario_codigo' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX idx_inventario_codigo ON inventario(codigo);
    PRINT '✓ Índice creado: idx_inventario_codigo';
END
ELSE
    PRINT '✓ Índice ya existe: idx_inventario_codigo';

-- Obras: estado (filtros por estado muy frecuentes)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_obras_estado' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX idx_obras_estado ON obras(estado);
    PRINT '✓ Índice creado: idx_obras_estado';
END
ELSE
    PRINT '✓ Índice ya existe: idx_obras_estado';

-- Usuarios: username (autenticación)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_usuarios_username' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX idx_usuarios_username ON usuarios(usuario);
    PRINT '✓ Índice creado: idx_usuarios_username';
END
ELSE
    PRINT '✓ Índice ya existe: idx_usuarios_username';

-- Pedidos: fecha de creación (ordenamientos y filtros)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pedidos_fecha' AND object_id = OBJECT_ID('pedidos'))
BEGIN
    CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_creacion);
    PRINT '✓ Índice creado: idx_pedidos_fecha';
END
ELSE
    PRINT '✓ Índice ya existe: idx_pedidos_fecha';

-- ============================================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================================================

-- Obras: responsable (filtros frecuentes)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_obras_responsable' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX idx_obras_responsable ON obras(responsable);
    PRINT '✓ Índice creado: idx_obras_responsable';
END
ELSE
    PRINT '✓ Índice ya existe: idx_obras_responsable';

-- Obras: fecha inicio (rangos de fechas)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_obras_fecha_inicio' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX idx_obras_fecha_inicio ON obras(fecha_inicio);
    PRINT '✓ Índice creado: idx_obras_fecha_inicio';
END
ELSE
    PRINT '✓ Índice ya existe: idx_obras_fecha_inicio';

-- Vidrios: tipo (filtros por tipo)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_vidrios_tipo' AND object_id = OBJECT_ID('vidrios'))
BEGIN
    CREATE INDEX idx_vidrios_tipo ON vidrios(tipo);
    PRINT '✓ Índice creado: idx_vidrios_tipo';
END
ELSE
    PRINT '✓ Índice ya existe: idx_vidrios_tipo';

-- Vidrios: proveedor (filtros por proveedor)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_vidrios_proveedor' AND object_id = OBJECT_ID('vidrios'))
BEGIN
    CREATE INDEX idx_vidrios_proveedor ON vidrios(proveedor);
    PRINT '✓ Índice creado: idx_vidrios_proveedor';
END
ELSE
    PRINT '✓ Índice ya existe: idx_vidrios_proveedor';

-- Herrajes: código (búsquedas de productos)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_herrajes_codigo' AND object_id = OBJECT_ID('herrajes'))
BEGIN
    CREATE INDEX idx_herrajes_codigo ON herrajes(codigo);
    PRINT '✓ Índice creado: idx_herrajes_codigo';
END
ELSE
    PRINT '✓ Índice ya existe: idx_herrajes_codigo';

-- Configuración: clave (acceso a configuraciones)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_configuracion_clave' AND object_id = OBJECT_ID('configuracion'))
BEGIN
    CREATE INDEX idx_configuracion_clave ON configuracion(clave);
    PRINT '✓ Índice creado: idx_configuracion_clave';
END
ELSE
    PRINT '✓ Índice ya existe: idx_configuracion_clave';

-- ============================================================================
-- ÍNDICES COMPUESTOS PARA CONSULTAS COMPLEJAS
-- ============================================================================

-- Inventario: categoría + estado (filtros combinados frecuentes)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_inventario_categoria_estado' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX idx_inventario_categoria_estado ON inventario(categoria, estado);
    PRINT '✓ Índice compuesto creado: idx_inventario_categoria_estado';
END
ELSE
    PRINT '✓ Índice compuesto ya existe: idx_inventario_categoria_estado';

-- Obras: estado + fecha_inicio (filtros de dashboard)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_obras_estado_fecha' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX idx_obras_estado_fecha ON obras(estado, fecha_inicio);
    PRINT '✓ Índice compuesto creado: idx_obras_estado_fecha';
END
ELSE
    PRINT '✓ Índice compuesto ya existe: idx_obras_estado_fecha';

-- Pedidos: estado + fecha (seguimiento de pedidos)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pedidos_estado_fecha' AND object_id = OBJECT_ID('pedidos'))
BEGIN
    CREATE INDEX idx_pedidos_estado_fecha ON pedidos(estado, fecha_creacion);
    PRINT '✓ Índice compuesto creado: idx_pedidos_estado_fecha';
END
ELSE
    PRINT '✓ Índice compuesto ya existe: idx_pedidos_estado_fecha';

-- ============================================================================
-- ÍNDICES PARA CLAVES FORÁNEAS (si no existen automáticamente)
-- ============================================================================

-- Vidrios por obra: vidrio_id
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_vidrios_obra_vidrio' AND object_id = OBJECT_ID('vidrios_obra'))
BEGIN
    CREATE INDEX idx_vidrios_obra_vidrio ON vidrios_obra(vidrio_id);
    PRINT '✓ Índice FK creado: idx_vidrios_obra_vidrio';
END
ELSE
    PRINT '✓ Índice FK ya existe: idx_vidrios_obra_vidrio';

-- Vidrios por obra: obra_id
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_vidrios_obra_obra' AND object_id = OBJECT_ID('vidrios_obra'))
BEGIN
    CREATE INDEX idx_vidrios_obra_obra ON vidrios_obra(obra_id);
    PRINT '✓ Índice FK creado: idx_vidrios_obra_obra';
END
ELSE
    PRINT '✓ Índice FK ya existe: idx_vidrios_obra_obra';

-- Herrajes por obra: herraje_id  
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_herrajes_obra_herraje' AND object_id = OBJECT_ID('herrajes_obra'))
BEGIN
    CREATE INDEX idx_herrajes_obra_herraje ON herrajes_obra(herraje_id);
    PRINT '✓ Índice FK creado: idx_herrajes_obra_herraje';
END
ELSE
    PRINT '✓ Índice FK ya existe: idx_herrajes_obra_herraje';

-- ============================================================================
-- ESTADÍSTICAS E INFORMACIÓN DE ÍNDICES
-- ============================================================================

PRINT '';
PRINT '📊 RESUMEN DE ÍNDICES CREADOS:';
PRINT '============================================';

-- Contar índices por tabla
SELECT 
    t.name AS tabla,
    COUNT(i.index_id) AS total_indices
FROM sys.tables t
LEFT JOIN sys.indexes i ON t.object_id = i.object_id
WHERE t.name IN ('inventario', 'obras', 'usuarios', 'pedidos', 'vidrios', 'herrajes', 'configuracion')
    AND i.type > 0  -- Excluir heap
GROUP BY t.name
ORDER BY t.name;

PRINT '';
PRINT '✅ OPTIMIZACIÓN DE PERFORMANCE COMPLETADA';
PRINT 'Los índices mejorarán significativamente el rendimiento de:';
PRINT '• Búsquedas por código de producto';
PRINT '• Filtros por estado de obras';  
PRINT '• Autenticación de usuarios';
PRINT '• Ordenamiento por fechas';
PRINT '• Consultas combinadas frecuentes';
PRINT '• Joins entre tablas relacionadas';
PRINT '';
PRINT '⚠️  NOTA: Monitorear el impacto en inserciones/actualizaciones';
PRINT '📈 Ejecutar análisis de performance después de implementar';