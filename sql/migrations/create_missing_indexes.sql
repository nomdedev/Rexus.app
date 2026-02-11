/*
 * ÍNDICES FALTANTES - Rexus.app
 * Auditoría de Base de Datos - FASE 1.2
 *
 * Crea índices recomendados en tablas de logística, RRHH y contabilidad
 *
 * Fecha: 2025-02-10
 * Prioridad: MEDIA
 */

-- ============================================
-- ÍNDICES PARA LOGÍSTICA
-- ============================================

USE [inventario];
GO

-- Índice para transportes por estado
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_transportes_estado')
BEGIN
    CREATE INDEX idx_transportes_estado
    ON transportes(estado);
    PRINT '✅ Índice idx_transportes_estado creado';
END
ELSE
    PRINT '⚠️ Índice idx_transportes_estado ya existe';
GO

-- Índice compuesto para entregas por obra y fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_entregas_obra_fecha')
BEGIN
    CREATE INDEX idx_entregas_obra_fecha
    ON entregas(obra_id, fecha_entrega);
    PRINT '✅ Índice idx_entregas_obra_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_entregas_obra_fecha ya existe';
GO

-- Índice para entregas por conductor
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_entregas_conductor')
BEGIN
    CREATE INDEX idx_entregas_conductor
    ON entregas(conductor_id);
    PRINT '✅ Índice idx_entregas_conductor creado';
END
ELSE
    PRINT '⚠️ Índice idx_entregas_conductor ya existe';
GO

-- Índice para detalle_entregas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_detalle_entregas_entrega')
BEGIN
    CREATE INDEX idx_detalle_entregas_entrega
    ON detalle_entregas(entrega_id);
    PRINT '✅ Índice idx_detalle_entregas_entrega creado';
END
ELSE
    PRINT '⚠️ Índice idx_detalle_entregas_entrega ya existe';
GO

-- ============================================
-- ÍNDICES PARA RECURSOS HUMANOS
-- ============================================

-- Índice para empleados por departamento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_empleados_departamento')
BEGIN
    CREATE INDEX idx_empleados_departamento
    ON empleados(departamento_id);
    PRINT '✅ Índice idx_empleados_departamento creado';
END
ELSE
    PRINT '⚠️ Índice idx_empleados_departamento ya existe';
GO

-- Índice para empleados activos
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_empleados_activo')
BEGIN
    CREATE INDEX idx_empleados_activo
    ON empleados(activo);
    PRINT '✅ Índice idx_empleados_activo creado';
END
ELSE
    PRINT '⚠️ Índice idx_empleados_activo ya existe';
GO

-- Índice para asistencias por fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_asistencias_fecha')
BEGIN
    CREATE INDEX idx_asistencias_fecha
    ON asistencias(fecha);
    PRINT '✅ Índice idx_asistencias_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_asistencias_fecha ya existe';
GO

-- Índice compuesto para asistencias por empleado y fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_asistencias_empleado_fecha')
BEGIN
    CREATE INDEX idx_asistencias_empleado_fecha
    ON asistencias(empleado_id, fecha);
    PRINT '✅ Índice idx_asistencias_empleado_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_asistencias_empleado_fecha ya existe';
GO

-- Índice para nómina por mes y año
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_nomina_mes_anio')
BEGIN
    CREATE INDEX idx_nomina_mes_anio
    ON nomina(mes, anio);
    PRINT '✅ Índice idx_nomina_mes_anio creado';
END
ELSE
    PRINT '⚠️ Índice idx_nomina_mes_anio ya existe';
GO

-- ============================================
-- ÍNDICES PARA CONTABILIDAD
-- ============================================

-- Índice para libro contable por fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_libro_contable_fecha')
BEGIN
    CREATE INDEX idx_libro_contable_fecha
    ON libro_contable(fecha_asiento);
    PRINT '✅ Índice idx_libro_contable_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_libro_contable_fecha ya existe';
GO

-- Índice para libro contable por tipo de asiento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_libro_contable_tipo')
BEGIN
    CREATE INDEX idx_libro_contable_tipo
    ON libro_contable(tipo_asiento);
    PRINT '✅ Índice idx_libro_contable_tipo creado';
END
ELSE
    PRINT '⚠️ Índice idx_libro_contable_tipo ya existe';
GO

-- Índice para recibos por obra
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_recibos_obra')
BEGIN
    CREATE INDEX idx_recibos_obra
    ON recibos(obra_id);
    PRINT '✅ Índice idx_recibos_obra creado';
END
ELSE
    PRINT '⚠️ Índice idx_recibos_obra ya existe';
GO

-- ============================================
-- ÍNDICES ADICIONALES PARA PERFORMANCE
-- ============================================

-- Índice para pagos de obra
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pagos_obra_fecha')
BEGIN
    CREATE INDEX idx_pagos_obra_fecha
    ON pagos_obra(obra_id, fecha_pago);
    PRINT '✅ Índice idx_pagos_obra_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_pagos_obra_fecha ya existe';
GO

-- Índice para pagos de materiales
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_pagos_materiales_fecha')
BEGIN
    CREATE INDEX idx_pagos_materiales_fecha
    ON pagos_materiales(fecha_pago);
    PRINT '✅ Índice idx_pagos_materiales_fecha creado';
END
ELSE
    PRINT '⚠️ Índice idx_pagos_materiales_fecha ya existe';
GO

-- Índice para herramientas por estado
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_herramientas_estado')
BEGIN
    CREATE INDEX idx_herramientas_estado
    ON herramientas(estado);
    PRINT '✅ Índice idx_herramientas_estado creado';
END
ELSE
    PRINT '⚠️ Índice idx_herramientas_estado ya existe';
GO

PRINT '';
PRINT '============================================';
PRINT '✅ CREACIÓN DE ÍNDICES COMPLETADA';
PRINT '============================================';
PRINT '';
