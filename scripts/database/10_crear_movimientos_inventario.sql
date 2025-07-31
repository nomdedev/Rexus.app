-- =====================================================
-- FASE 2.4: Crear tabla movimientos_inventario unificada
-- Reemplaza: movimientos_stock y sistemas dispersos de tracking
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO CREACIÓN: Tabla movimientos_inventario unificada ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- ==============================================
-- CREAR TABLA MOVIMIENTOS_INVENTARIO UNIFICADA
-- ==============================================

IF OBJECT_ID('movimientos_inventario', 'U') IS NULL
BEGIN
    CREATE TABLE movimientos_inventario (
        id BIGINT IDENTITY(1,1) PRIMARY KEY, -- BIGINT para alto volumen
        
        -- Product Reference
        producto_id INT NOT NULL, -- FOREIGN KEY REFERENCES productos(id)
        codigo_producto NVARCHAR(50) NOT NULL, -- Snapshot para auditoría
        descripcion_producto NVARCHAR(255) NOT NULL,
        categoria_producto NVARCHAR(50) NOT NULL,
        
        -- Movement Classification
        tipo_movimiento NVARCHAR(50) NOT NULL CHECK (tipo_movimiento IN (
            'ENTRADA', 'SALIDA', 'AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO', 
            'RESERVA', 'LIBERACION_RESERVA', 'TRANSFERENCIA_ENTRADA', 'TRANSFERENCIA_SALIDA',
            'MERMA', 'DEVOLUCION', 'CONSUMO_OBRA', 'RECEPCION_COMPRA'
        )),
        subtipo_movimiento NVARCHAR(50), -- Clasificación más específica
        origen_movimiento NVARCHAR(50) DEFAULT 'MANUAL' CHECK (origen_movimiento IN (
            'MANUAL', 'AUTOMATICO', 'PEDIDO', 'OBRA', 'AJUSTE', 'SISTEMA', 'IMPORTACION'
        )),
        
        -- Quantity & Stock Impact
        cantidad DECIMAL(10,3) NOT NULL,
        unidad_medida NVARCHAR(20) NOT NULL,
        factor_conversion DECIMAL(10,6) DEFAULT 1, -- Para conversiones
        cantidad_base AS (cantidad * factor_conversion) PERSISTED, -- Cantidad en unidad base
        
        -- Stock Levels (snapshots)
        stock_anterior DECIMAL(10,3) NOT NULL,
        stock_nuevo DECIMAL(10,3) NOT NULL,
        stock_verificado AS (
            CASE tipo_movimiento
                WHEN 'ENTRADA' THEN stock_anterior + cantidad
                WHEN 'SALIDA' THEN stock_anterior - cantidad
                WHEN 'AJUSTE_POSITIVO' THEN stock_anterior + cantidad
                WHEN 'AJUSTE_NEGATIVO' THEN stock_anterior - cantidad
                ELSE stock_nuevo
            END
        ) PERSISTED,
        
        -- Reserved Stock Impact
        reserva_anterior DECIMAL(10,3) DEFAULT 0,
        reserva_nueva DECIMAL(10,3) DEFAULT 0,
        impacto_reserva AS (reserva_nueva - reserva_anterior) PERSISTED,
        
        -- Pricing & Costing
        precio_unitario DECIMAL(18,2) DEFAULT 0, -- Precio al momento del movimiento
        costo_unitario DECIMAL(18,2) DEFAULT 0, -- Costo al momento del movimiento
        valor_total_movimiento AS (cantidad * precio_unitario) PERSISTED,
        costo_total_movimiento AS (cantidad * costo_unitario) PERSISTED,
        
        -- Reference Documents & Context
        documento_referencia NVARCHAR(100), -- Número de documento origen
        tipo_documento NVARCHAR(50), -- PEDIDO, FACTURA, REMITO, ORDEN, etc.
        obra_id INT, -- FOREIGN KEY REFERENCES obras(id) - si aplica
        pedido_id INT, -- FOREIGN KEY REFERENCES pedidos_consolidado(id) - si aplica
        proveedor NVARCHAR(100), -- Si es de/hacia proveedor
        cliente NVARCHAR(100), -- Si es de/hacia cliente
        
        -- Location & Logistics
        ubicacion_origen NVARCHAR(100),
        ubicacion_destino NVARCHAR(100),
        deposito_origen NVARCHAR(100),
        deposito_destino NVARCHAR(100),
        responsable_movimiento NVARCHAR(100),
        autorizado_por NVARCHAR(100),
        
        -- Business Context
        motivo NVARCHAR(255), -- Razón del movimiento
        observaciones NTEXT,
        notas_internas NTEXT, -- Notas no visibles externamente
        
        -- Quality & Compliance
        lote_numero NVARCHAR(50), -- Número de lote
        fecha_vencimiento DATE, -- Si aplica
        fecha_fabricacion DATE, -- Si aplica
        certificado_calidad NVARCHAR(100),
        requiere_inspeccion BIT DEFAULT 0,
        inspeccion_aprobada BIT DEFAULT 1,
        
        -- Timing & Scheduling
        fecha_movimiento DATETIME NOT NULL DEFAULT GETDATE(),
        fecha_programada DATETIME, -- Cuándo estaba programado
        fecha_confirmacion DATETIME, -- Cuándo se confirmó
        fecha_contabilizacion DATE, -- Para cierre contable
        
        -- Status & Workflow
        estado NVARCHAR(50) DEFAULT 'CONFIRMADO' CHECK (estado IN (
            'BORRADOR', 'PENDIENTE', 'CONFIRMADO', 'PROCESADO', 'CANCELADO', 'REVERTIDO'
        )),
        requiere_aprobacion BIT DEFAULT 0,
        aprobado_por INT, -- Usuario que aprobó
        fecha_aprobacion DATETIME,
        
        -- Error Handling & Corrections
        es_correccion BIT DEFAULT 0,
        movimiento_original_id BIGINT, -- FOREIGN KEY REFERENCES movimientos_inventario(id)
        motivo_correccion NVARCHAR(255),
        
        -- Integration & External Systems
        sincronizado_erp BIT DEFAULT 0,
        id_erp_externo NVARCHAR(100),
        fecha_sincronizacion DATETIME,
        sistema_origen NVARCHAR(50) DEFAULT 'REXUS',
        
        -- Audit & Control
        usuario_movimiento INT NOT NULL, -- Usuario que registró el movimiento
        usuario_autorizacion INT, -- Usuario que autorizó (si diferente)
        ip_address NVARCHAR(45), -- IP desde donde se registró
        session_id NVARCHAR(100), -- Sesión del usuario
        
        -- Additional Tracking
        numero_serie NVARCHAR(100), -- Para productos seriados
        codigo_barras_movimiento NVARCHAR(100),
        peso_total DECIMAL(10,3), -- Peso total del movimiento
        volumen_total DECIMAL(10,3), -- Volumen total
        
        -- Performance Metrics
        tiempo_procesamiento_ms INT, -- Tiempo que tardó en procesarse
        metodo_captura NVARCHAR(50) DEFAULT 'MANUAL', -- MANUAL, SCANNER, API, etc.
        
        -- Control Fields
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE(),
        usuario_modificacion INT,
        
        -- Version Control
        version INT DEFAULT 1,
        hash_integridad NVARCHAR(64), -- Para verificar integridad
        
        -- Constraints
        CONSTRAINT CK_movimientos_cantidad_positiva CHECK (cantidad > 0),
        CONSTRAINT CK_movimientos_stock_logico CHECK (
            (tipo_movimiento IN ('ENTRADA', 'AJUSTE_POSITIVO') AND stock_nuevo >= stock_anterior) OR
            (tipo_movimiento IN ('SALIDA', 'AJUSTE_NEGATIVO') AND stock_nuevo <= stock_anterior) OR
            (tipo_movimiento NOT IN ('ENTRADA', 'SALIDA', 'AJUSTE_POSITIVO', 'AJUSTE_NEGATIVO'))
        ),
        CONSTRAINT FK_movimientos_correccion FOREIGN KEY (movimiento_original_id) REFERENCES movimientos_inventario(id)
    );
    
    PRINT 'Tabla movimientos_inventario creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla movimientos_inventario ya existe - verificando estructura';
    
    -- Verificar y agregar columnas faltantes
    IF COL_LENGTH('movimientos_inventario', 'hash_integridad') IS NULL
        ALTER TABLE movimientos_inventario ADD hash_integridad NVARCHAR(64);
    
    IF COL_LENGTH('movimientos_inventario', 'tiempo_procesamiento_ms') IS NULL
        ALTER TABLE movimientos_inventario ADD tiempo_procesamiento_ms INT;
END
GO

-- ==============================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- ==============================================

PRINT 'Creando índices de optimización...';

-- Índice principal por producto y fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_producto_fecha')
    CREATE INDEX IX_movimientos_producto_fecha ON movimientos_inventario(producto_id, fecha_movimiento DESC);
GO

-- Índice por tipo de movimiento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_tipo_fecha')
    CREATE INDEX IX_movimientos_tipo_fecha ON movimientos_inventario(tipo_movimiento, fecha_movimiento DESC);
GO

-- Índice por obra
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_obra')
    CREATE INDEX IX_movimientos_obra ON movimientos_inventario(obra_id, fecha_movimiento DESC)
    WHERE obra_id IS NOT NULL;
GO

-- Índice por pedido
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_pedido')
    CREATE INDEX IX_movimientos_pedido ON movimientos_inventario(pedido_id, fecha_movimiento DESC)
    WHERE pedido_id IS NOT NULL;
GO

-- Índice por documento referencia
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_documento')
    CREATE INDEX IX_movimientos_documento ON movimientos_inventario(documento_referencia, tipo_documento);
GO

-- Índice por usuario y fecha (para auditoría)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_usuario_fecha')
    CREATE INDEX IX_movimientos_usuario_fecha ON movimientos_inventario(usuario_movimiento, fecha_movimiento DESC);
GO

-- Índice por estado y fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_estado')
    CREATE INDEX IX_movimientos_estado ON movimientos_inventario(estado, fecha_movimiento DESC)
    WHERE estado != 'CONFIRMADO'; -- Solo indexar estados no normales
GO

-- Índice por categoría producto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_movimientos_categoria')
    CREATE INDEX IX_movimientos_categoria ON movimientos_inventario(categoria_producto, fecha_movimiento DESC);
GO

-- ==============================================
-- CREAR VISTAS ESPECIALIZADAS
-- ==============================================

PRINT 'Creando vistas especializadas...';

-- Vista para movimientos recientes
IF OBJECT_ID('v_movimientos_recientes', 'V') IS NOT NULL
    DROP VIEW v_movimientos_recientes;
GO

CREATE VIEW v_movimientos_recientes AS
SELECT TOP 1000
    mi.id,
    mi.producto_id,
    mi.codigo_producto,
    mi.descripcion_producto,
    mi.categoria_producto,
    mi.tipo_movimiento,
    mi.cantidad,
    mi.unidad_medida,
    mi.stock_anterior,
    mi.stock_nuevo,
    mi.documento_referencia,
    mi.obra_id,
    mi.motivo,
    mi.usuario_movimiento,
    mi.fecha_movimiento,
    CASE 
        WHEN mi.tipo_movimiento IN ('ENTRADA', 'AJUSTE_POSITIVO') THEN 'POSITIVO'
        WHEN mi.tipo_movimiento IN ('SALIDA', 'AJUSTE_NEGATIVO') THEN 'NEGATIVO'
        ELSE 'NEUTRO'
    END as impacto_stock
FROM movimientos_inventario mi
WHERE mi.activo = 1 AND mi.estado = 'CONFIRMADO'
ORDER BY mi.fecha_movimiento DESC;
GO

-- Vista para análisis de stock por producto
IF OBJECT_ID('v_analisis_stock_producto', 'V') IS NOT NULL
    DROP VIEW v_analisis_stock_producto;
GO

CREATE VIEW v_analisis_stock_producto AS
SELECT 
    mi.producto_id,
    mi.codigo_producto,
    mi.descripcion_producto,
    mi.categoria_producto,
    COUNT(*) as total_movimientos,
    SUM(CASE WHEN mi.tipo_movimiento IN ('ENTRADA', 'AJUSTE_POSITIVO') THEN mi.cantidad ELSE 0 END) as total_entradas,
    SUM(CASE WHEN mi.tipo_movimiento IN ('SALIDA', 'AJUSTE_NEGATIVO') THEN mi.cantidad ELSE 0 END) as total_salidas,
    SUM(CASE WHEN mi.tipo_movimiento = 'ENTRADA' THEN mi.cantidad ELSE 0 END) as entradas_normales,
    SUM(CASE WHEN mi.tipo_movimiento = 'SALIDA' THEN mi.cantidad ELSE 0 END) as salidas_normales,
    SUM(CASE WHEN mi.tipo_movimiento LIKE 'AJUSTE%' THEN mi.cantidad ELSE 0 END) as total_ajustes,
    AVG(CASE WHEN mi.tipo_movimiento = 'ENTRADA' THEN mi.cantidad END) as promedio_entrada,
    AVG(CASE WHEN mi.tipo_movimiento = 'SALIDA' THEN mi.cantidad END) as promedio_salida,
    MAX(mi.fecha_movimiento) as ultimo_movimiento,
    MIN(mi.fecha_movimiento) as primer_movimiento,
    COUNT(DISTINCT CAST(mi.fecha_movimiento AS DATE)) as dias_con_movimiento
FROM movimientos_inventario mi
WHERE mi.activo = 1 
    AND mi.estado = 'CONFIRMADO'
    AND mi.fecha_movimiento >= DATEADD(MONTH, -6, GETDATE()) -- Últimos 6 meses
GROUP BY mi.producto_id, mi.codigo_producto, mi.descripcion_producto, mi.categoria_producto;
GO

-- Vista para movimientos por obra
IF OBJECT_ID('v_movimientos_por_obra', 'V') IS NOT NULL
    DROP VIEW v_movimientos_por_obra;
GO

CREATE VIEW v_movimientos_por_obra AS
SELECT 
    mi.obra_id,
    mi.categoria_producto,
    COUNT(*) as total_movimientos,
    COUNT(DISTINCT mi.producto_id) as productos_diferentes,
    SUM(CASE WHEN mi.tipo_movimiento = 'CONSUMO_OBRA' THEN mi.cantidad ELSE 0 END) as total_consumido,
    SUM(CASE WHEN mi.tipo_movimiento = 'DEVOLUCION' THEN mi.cantidad ELSE 0 END) as total_devuelto,
    SUM(mi.valor_total_movimiento) as valor_total_movimientos,
    AVG(mi.cantidad) as cantidad_promedio_movimiento,
    MIN(mi.fecha_movimiento) as primer_movimiento,
    MAX(mi.fecha_movimiento) as ultimo_movimiento,
    COUNT(CASE WHEN mi.fecha_movimiento >= DATEADD(DAY, -7, GETDATE()) THEN 1 END) as movimientos_ultima_semana
FROM movimientos_inventario mi
WHERE mi.activo = 1 
    AND mi.estado = 'CONFIRMADO'
    AND mi.obra_id IS NOT NULL
GROUP BY mi.obra_id, mi.categoria_producto;
GO

-- Vista para dashboard de movimientos
IF OBJECT_ID('v_dashboard_movimientos', 'V') IS NOT NULL
    DROP VIEW v_dashboard_movimientos;
GO

CREATE VIEW v_dashboard_movimientos AS
SELECT 
    COUNT(*) as total_movimientos_hoy,
    COUNT(CASE WHEN mi.tipo_movimiento IN ('ENTRADA', 'RECEPCION_COMPRA') THEN 1 END) as entradas_hoy,
    COUNT(CASE WHEN mi.tipo_movimiento IN ('SALIDA', 'CONSUMO_OBRA') THEN 1 END) as salidas_hoy,
    COUNT(CASE WHEN mi.tipo_movimiento LIKE 'AJUSTE%' THEN 1 END) as ajustes_hoy,
    COUNT(DISTINCT mi.producto_id) as productos_movidos_hoy,
    COUNT(DISTINCT mi.usuario_movimiento) as usuarios_activos_hoy,
    COUNT(DISTINCT mi.obra_id) as obras_con_movimientos_hoy,
    SUM(mi.valor_total_movimiento) as valor_total_movimientos_hoy,
    AVG(mi.tiempo_procesamiento_ms) as tiempo_promedio_procesamiento,
    COUNT(CASE WHEN mi.estado = 'PENDIENTE' THEN 1 END) as movimientos_pendientes,
    COUNT(CASE WHEN mi.requiere_aprobacion = 1 AND mi.aprobado_por IS NULL THEN 1 END) as pendientes_aprobacion
FROM movimientos_inventario mi
WHERE mi.activo = 1 
    AND CAST(mi.fecha_movimiento AS DATE) = CAST(GETDATE() AS DATE);
GO

-- ==============================================
-- CREAR FUNCIONES ÚTILES
-- ==============================================

PRINT 'Creando funciones de utilidad...';

-- Función para calcular stock a una fecha específica
IF OBJECT_ID('fn_stock_historico', 'FN') IS NOT NULL
    DROP FUNCTION fn_stock_historico;
GO

CREATE FUNCTION fn_stock_historico(@producto_id INT, @fecha DATETIME)
RETURNS DECIMAL(10,3)
AS
BEGIN
    DECLARE @stock_historico DECIMAL(10,3) = 0;
    
    -- Buscar el último movimiento antes o en la fecha especificada
    SELECT TOP 1 @stock_historico = stock_nuevo
    FROM movimientos_inventario
    WHERE producto_id = @producto_id
        AND fecha_movimiento <= @fecha
        AND estado = 'CONFIRMADO'
        AND activo = 1
    ORDER BY fecha_movimiento DESC, id DESC;
    
    RETURN ISNULL(@stock_historico, 0);
END
GO

-- Función para generar hash de integridad de movimiento
IF OBJECT_ID('fn_hash_movimiento', 'FN') IS NOT NULL
    DROP FUNCTION fn_hash_movimiento;
GO

CREATE FUNCTION fn_hash_movimiento(
    @producto_id INT,
    @tipo_movimiento NVARCHAR(50),
    @cantidad DECIMAL(10,3),
    @fecha_movimiento DATETIME,
    @usuario_movimiento INT
)
RETURNS NVARCHAR(64)
AS
BEGIN
    DECLARE @cadena NVARCHAR(500);
    SET @cadena = CONCAT(
        CAST(@producto_id AS NVARCHAR),
        @tipo_movimiento,
        CAST(@cantidad AS NVARCHAR),
        FORMAT(@fecha_movimiento, 'yyyy-MM-dd HH:mm:ss.fff'),
        CAST(@usuario_movimiento AS NVARCHAR)
    );
    
    RETURN CONVERT(NVARCHAR(64), HASHBYTES('SHA2_256', @cadena), 2);
END
GO

-- ==============================================
-- CREAR PROCEDIMIENTOS ALMACENADOS
-- ==============================================

PRINT 'Creando procedimientos almacenados...';

-- Procedimiento para registrar movimiento de inventario
IF OBJECT_ID('sp_registrar_movimiento', 'P') IS NOT NULL
    DROP PROCEDURE sp_registrar_movimiento;
GO

CREATE PROCEDURE sp_registrar_movimiento
    @producto_id INT,
    @tipo_movimiento NVARCHAR(50),
    @cantidad DECIMAL(10,3),
    @motivo NVARCHAR(255) = NULL,
    @documento_referencia NVARCHAR(100) = NULL,
    @obra_id INT = NULL,
    @pedido_id INT = NULL,
    @usuario_movimiento INT,
    @ubicacion_origen NVARCHAR(100) = NULL,
    @ubicacion_destino NVARCHAR(100) = NULL,
    @observaciones NTEXT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @stock_actual DECIMAL(10,3);
    DECLARE @stock_nuevo DECIMAL(10,3);
    DECLARE @codigo_producto NVARCHAR(50);
    DECLARE @descripcion_producto NVARCHAR(255);
    DECLARE @categoria_producto NVARCHAR(50);
    DECLARE @unidad_medida NVARCHAR(20);
    DECLARE @precio_unitario DECIMAL(18,2);
    DECLARE @hash_integridad NVARCHAR(64);
    DECLARE @fecha_movimiento DATETIME = GETDATE();
    
    -- Obtener datos del producto
    SELECT 
        @stock_actual = stock_actual,
        @codigo_producto = codigo,
        @descripcion_producto = descripcion,
        @categoria_producto = categoria,
        @unidad_medida = unidad_medida,
        @precio_unitario = precio_unitario
    FROM productos 
    WHERE id = @producto_id AND activo = 1;
    
    IF @stock_actual IS NULL
    BEGIN
        RAISERROR('Producto no encontrado o inactivo', 16, 1);
        RETURN -1;
    END
    
    -- Calcular nuevo stock
    SET @stock_nuevo = 
        CASE @tipo_movimiento
            WHEN 'ENTRADA' THEN @stock_actual + @cantidad
            WHEN 'SALIDA' THEN @stock_actual - @cantidad
            WHEN 'AJUSTE_POSITIVO' THEN @stock_actual + @cantidad
            WHEN 'AJUSTE_NEGATIVO' THEN @stock_actual - @cantidad
            ELSE @stock_actual
        END;
    
    -- Validar que no quede stock negativo
    IF @stock_nuevo < 0
    BEGIN
        RAISERROR('El movimiento resultaría en stock negativo', 16, 1);
        RETURN -2;
    END
    
    -- Generar hash de integridad
    SET @hash_integridad = dbo.fn_hash_movimiento(@producto_id, @tipo_movimiento, @cantidad, @fecha_movimiento, @usuario_movimiento);
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Insertar movimiento
        INSERT INTO movimientos_inventario (
            producto_id, codigo_producto, descripcion_producto, categoria_producto,
            tipo_movimiento, cantidad, unidad_medida, stock_anterior, stock_nuevo,
            precio_unitario, documento_referencia, obra_id, pedido_id,
            ubicacion_origen, ubicacion_destino, motivo, observaciones,
            usuario_movimiento, fecha_movimiento, hash_integridad
        )
        VALUES (
            @producto_id, @codigo_producto, @descripcion_producto, @categoria_producto,
            @tipo_movimiento, @cantidad, @unidad_medida, @stock_actual, @stock_nuevo,
            @precio_unitario, @documento_referencia, @obra_id, @pedido_id,
            @ubicacion_origen, @ubicacion_destino, @motivo, @observaciones,
            @usuario_movimiento, @fecha_movimiento, @hash_integridad
        );
        
        -- Actualizar stock del producto
        UPDATE productos 
        SET stock_actual = @stock_nuevo,
            fecha_ultimo_movimiento = @fecha_movimiento
        WHERE id = @producto_id;
        
        COMMIT TRANSACTION;
        
        RETURN @@IDENTITY; -- Retornar ID del movimiento creado
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

PRINT '';
PRINT '=== TABLA MOVIMIENTOS_INVENTARIO UNIFICADA CREADA EXITOSAMENTE ===';
PRINT 'Tabla creada: 1';
PRINT 'Índices creados: 8';
PRINT 'Vistas creadas: 4';
PRINT 'Funciones creadas: 2';
PRINT 'Procedimientos creados: 1';
PRINT '';
PRINT 'Características principales:';
PRINT '- Trazabilidad completa de movimientos de inventario';
PRINT '- Soporte para múltiples tipos de movimiento';
PRINT '- Integración con obras y pedidos';
PRINT '- Control de integridad con hash';
PRINT '- Análisis histórico de stock';
PRINT '- Dashboard de movimientos en tiempo real';
PRINT '- Procedimientos optimizados para registro';
PRINT '';
PRINT 'FASE 2 COMPLETADA - Sistema de operaciones consolidado';
PRINT 'Próximo paso: Ejecutar scripts de FASE 3 (Actualización de modelos)';
GO