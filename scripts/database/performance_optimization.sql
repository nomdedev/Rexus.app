
-- ====================================================
-- SCRIPT DE OPTIMIZACIÓN DE RENDIMIENTO - REXUS.APP
-- Índices para mejorar rendimiento de consultas
-- ====================================================

-- Verificar si un índice existe antes de crearlo
-- (Compatible con SQL Server)


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_estado' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX IX_usuarios_estado ON usuarios (estado);
    PRINT 'Índice IX_usuarios_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_usuarios_estado ya existe';
END
GO


-- Campo fecha usado para ordenamiento cronológico y filtros temporales
-- Impacto: Medio - Mejora consultas temporales y paginación
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_fecha_creacion' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX IX_usuarios_fecha_creacion ON usuarios (fecha_creacion);
    PRINT 'Índice IX_usuarios_fecha_creacion creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_usuarios_fecha_creacion ya existe';
END
GO


-- Combinación común en filtros por estado con ordenamiento temporal
-- Impacto: Medio - Optimiza consultas combinadas estado-fecha
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_estado_fecha_creacion' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX IX_usuarios_estado_fecha_creacion ON usuarios (estado, fecha_creacion);
    PRINT 'Índice IX_usuarios_estado_fecha_creacion creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_usuarios_estado_fecha_creacion ya existe';
END
GO


-- Campo de identificación único usado frecuentemente en búsquedas
-- Impacto: Alto - Mejora significativa en consultas por código
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_codigo' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_codigo ON inventario (codigo);
    PRINT 'Índice IX_inventario_codigo creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_codigo ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_estado' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_estado ON inventario (estado);
    PRINT 'Índice IX_inventario_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_estado ya existe';
END
GO


-- Campo fecha usado para ordenamiento cronológico y filtros temporales
-- Impacto: Medio - Mejora consultas temporales y paginación
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_fecha_creacion' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_fecha_creacion ON inventario (fecha_creacion);
    PRINT 'Índice IX_inventario_fecha_creacion creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_fecha_creacion ya existe';
END
GO


-- Combinación común en filtros por estado con ordenamiento temporal
-- Impacto: Medio - Optimiza consultas combinadas estado-fecha
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_estado_fecha_creacion' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_estado_fecha_creacion ON inventario (estado, fecha_creacion);
    PRINT 'Índice IX_inventario_estado_fecha_creacion creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_estado_fecha_creacion ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_compras_estado' AND object_id = OBJECT_ID('compras'))
BEGIN
    CREATE INDEX IX_compras_estado ON compras (estado);
    PRINT 'Índice IX_compras_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_compras_estado ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_mantenimientos_estado' AND object_id = OBJECT_ID('mantenimientos'))
BEGIN
    CREATE INDEX IX_mantenimientos_estado ON mantenimientos (estado);
    PRINT 'Índice IX_mantenimientos_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_mantenimientos_estado ya existe';
END
GO


-- Campo de identificación único usado frecuentemente en búsquedas
-- Impacto: Alto - Mejora significativa en consultas por código
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_equipos_codigo' AND object_id = OBJECT_ID('equipos'))
BEGIN
    CREATE INDEX IX_equipos_codigo ON equipos (codigo);
    PRINT 'Índice IX_equipos_codigo creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_equipos_codigo ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_equipos_estado' AND object_id = OBJECT_ID('equipos'))
BEGIN
    CREATE INDEX IX_equipos_estado ON equipos (estado);
    PRINT 'Índice IX_equipos_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_equipos_estado ya existe';
END
GO


-- Campo de identificación único usado frecuentemente en búsquedas
-- Impacto: Alto - Mejora significativa en consultas por código
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_obras_codigo' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX IX_obras_codigo ON obras (codigo);
    PRINT 'Índice IX_obras_codigo creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_obras_codigo ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_obras_estado' AND object_id = OBJECT_ID('obras'))
BEGIN
    CREATE INDEX IX_obras_estado ON obras (estado);
    PRINT 'Índice IX_obras_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_obras_estado ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_estado' AND object_id = OBJECT_ID('pedidos'))
BEGIN
    CREATE INDEX IX_pedidos_estado ON pedidos (estado);
    PRINT 'Índice IX_pedidos_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_pedidos_estado ya existe';
END
GO


-- Campo de identificación único usado frecuentemente en búsquedas
-- Impacto: Alto - Mejora significativa en consultas por código
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_vidrios_codigo' AND object_id = OBJECT_ID('vidrios'))
BEGIN
    CREATE INDEX IX_vidrios_codigo ON vidrios (codigo);
    PRINT 'Índice IX_vidrios_codigo creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_vidrios_codigo ya existe';
END
GO


-- Campo de identificación único usado frecuentemente en búsquedas
-- Impacto: Alto - Mejora significativa en consultas por código
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_herrajes_codigo' AND object_id = OBJECT_ID('herrajes'))
BEGIN
    CREATE INDEX IX_herrajes_codigo ON herrajes (codigo);
    PRINT 'Índice IX_herrajes_codigo creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_herrajes_codigo ya existe';
END
GO


-- Campo estado usado frecuentemente para filtrar registros activos/inactivos
-- Impacto: Alto - Mejora filtros por estado
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_logistica_estado' AND object_id = OBJECT_ID('logistica'))
BEGIN
    CREATE INDEX IX_logistica_estado ON logistica (estado);
    PRINT 'Índice IX_logistica_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_logistica_estado ya existe';
END
GO


-- Campo username usado en autenticación (búsquedas frecuentes)
-- Impacto: Crítico - Mejora tiempo de login significativamente
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_username' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX IX_usuarios_username ON usuarios (username);
    PRINT 'Índice IX_usuarios_username creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_usuarios_username ya existe';
END
GO


-- Campo email usado para recuperación de contraseñas y validación
-- Impacto: Alto - Mejora validaciones y recuperación de cuenta
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_usuarios_email' AND object_id = OBJECT_ID('usuarios'))
BEGIN
    CREATE INDEX IX_usuarios_email ON usuarios (email);
    PRINT 'Índice IX_usuarios_email creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_usuarios_email ya existe';
END
GO


-- Consultas frecuentes por categoría y estado para reportes de stock
-- Impacto: Alto - Optimiza reportes de inventario por categoría
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_categoria_estado' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_categoria_estado ON inventario (categoria, estado);
    PRINT 'Índice IX_inventario_categoria_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_categoria_estado ya existe';
END
GO


-- Búsquedas por proveedor para gestión de compras
-- Impacto: Medio - Mejora búsquedas por proveedor
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_inventario_proveedor' AND object_id = OBJECT_ID('inventario'))
BEGIN
    CREATE INDEX IX_inventario_proveedor ON inventario (proveedor);
    PRINT 'Índice IX_inventario_proveedor creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_inventario_proveedor ya existe';
END
GO


-- Búsquedas por número de orden para seguimiento
-- Impacto: Alto - Mejora búsquedas de órdenes específicas
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_compras_numero_orden' AND object_id = OBJECT_ID('compras'))
BEGIN
    CREATE INDEX IX_compras_numero_orden ON compras (numero_orden);
    PRINT 'Índice IX_compras_numero_orden creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_compras_numero_orden ya existe';
END
GO


-- Reportes por proveedor filtrados por estado
-- Impacto: Medio - Optimiza reportes de compras por proveedor
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_compras_proveedor_estado' AND object_id = OBJECT_ID('compras'))
BEGIN
    CREATE INDEX IX_compras_proveedor_estado ON compras (proveedor, estado);
    PRINT 'Índice IX_compras_proveedor_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_compras_proveedor_estado ya existe';
END
GO


-- Consultas por equipo para historial de mantenimiento
-- Impacto: Alto - Mejora consultas de historial por equipo
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_mantenimientos_equipo_id' AND object_id = OBJECT_ID('mantenimientos'))
BEGIN
    CREATE INDEX IX_mantenimientos_equipo_id ON mantenimientos (equipo_id);
    PRINT 'Índice IX_mantenimientos_equipo_id creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_mantenimientos_equipo_id ya existe';
END
GO


-- Consultas para calendario de mantenimientos pendientes
-- Impacto: Alto - Optimiza calendario de mantenimientos
-- Prioridad: HIGH
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_mantenimientos_fecha_programada_estado' AND object_id = OBJECT_ID('mantenimientos'))
BEGIN
    CREATE INDEX IX_mantenimientos_fecha_programada_estado ON mantenimientos (fecha_programada, estado);
    PRINT 'Índice IX_mantenimientos_fecha_programada_estado creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_mantenimientos_fecha_programada_estado ya existe';
END
GO


-- Consultas de auditoría por usuario en rangos de tiempo
-- Impacto: Medio - Mejora consultas de auditoría
-- Prioridad: MEDIUM
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_usuario_fecha' AND object_id = OBJECT_ID('auditoria'))
BEGIN
    CREATE INDEX IX_auditoria_usuario_fecha ON auditoria (usuario, fecha);
    PRINT 'Índice IX_auditoria_usuario_fecha creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_auditoria_usuario_fecha ya existe';
END
GO


-- Filtros por tipo de acción en reportes de auditoría
-- Impacto: Bajo - Mejora filtros por tipo de acción
-- Prioridad: LOW
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_accion' AND object_id = OBJECT_ID('auditoria'))
BEGIN
    CREATE INDEX IX_auditoria_accion ON auditoria (accion);
    PRINT 'Índice IX_auditoria_accion creado exitosamente';
END
ELSE
BEGIN
    PRINT 'Índice IX_auditoria_accion ya existe';
END
GO

