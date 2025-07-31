-- =====================================================
-- FASE 2.3: Crear tabla productos_obra unificada
-- Reemplaza: materiales_por_obra, herrajes_obra, vidrios_obra
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO CREACIÓN: Tabla productos_obra unificada ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- ==============================================
-- CREAR TABLA PRODUCTOS_OBRA UNIFICADA
-- ==============================================

IF OBJECT_ID('productos_obra', 'U') IS NULL
BEGIN
    CREATE TABLE productos_obra (
        id INT IDENTITY(1,1) PRIMARY KEY,
        
        -- Relationships
        obra_id INT NOT NULL, -- FOREIGN KEY REFERENCES obras(id)
        producto_id INT NOT NULL, -- FOREIGN KEY REFERENCES productos(id)
        pedido_id INT, -- FOREIGN KEY REFERENCES pedidos_consolidado(id) - opcional
        
        -- Product Snapshot (para auditoría)
        codigo_producto NVARCHAR(50) NOT NULL,
        descripcion_producto NVARCHAR(255) NOT NULL,
        categoria_producto NVARCHAR(50) NOT NULL,
        
        -- Quantity Management
        cantidad_requerida DECIMAL(10,3) NOT NULL CHECK (cantidad_requerida > 0),
        cantidad_asignada DECIMAL(10,3) DEFAULT 0 CHECK (cantidad_asignada >= 0),
        cantidad_utilizada DECIMAL(10,3) DEFAULT 0 CHECK (cantidad_utilizada >= 0),
        cantidad_pendiente AS (cantidad_requerida - cantidad_asignada) PERSISTED,
        cantidad_disponible AS (cantidad_asignada - cantidad_utilizada) PERSISTED,
        
        -- Units & Measurements
        unidad_medida NVARCHAR(20) NOT NULL DEFAULT 'UND',
        factor_conversion DECIMAL(10,6) DEFAULT 1, -- Para conversiones de unidades
        
        -- Project Context
        etapa_obra NVARCHAR(100), -- En qué etapa se usa (ESTRUCTURA, CERRAMIENTO, etc.)
        ubicacion_obra NVARCHAR(100), -- Dónde se instala en la obra
        sector_obra NVARCHAR(100), -- Sector específico de la obra
        nivel_obra NVARCHAR(50), -- Planta baja, primer piso, etc.
        
        -- Scheduling
        fecha_requerida DATE, -- Cuándo se necesita en obra
        fecha_asignacion DATETIME, -- Cuándo se asignó
        fecha_entrega_obra DATE, -- Cuándo se entregó en obra
        fecha_instalacion DATE, -- Cuándo se instaló
        
        -- Status Management
        estado NVARCHAR(50) DEFAULT 'PLANIFICADO' CHECK (estado IN (
            'PLANIFICADO', 'SOLICITADO', 'APROBADO', 'ASIGNADO', 'EN_TRANSITO', 
            'EN_OBRA', 'INSTALADO', 'COMPLETADO', 'CANCELADO'
        )),
        prioridad NVARCHAR(20) DEFAULT 'NORMAL' CHECK (prioridad IN ('BAJA', 'NORMAL', 'ALTA', 'CRITICA')),
        
        -- Costing & Budgeting
        precio_unitario_presupuesto DECIMAL(18,2) DEFAULT 0, -- Precio planificado
        precio_unitario_real DECIMAL(18,2) DEFAULT 0, -- Precio real pagado
        costo_total_presupuestado AS (cantidad_requerida * precio_unitario_presupuesto) PERSISTED,
        costo_total_real AS (cantidad_utilizada * precio_unitario_real) PERSISTED,
        variacion_presupuesto AS (
            CASE 
                WHEN precio_unitario_presupuesto > 0 THEN 
                    ((precio_unitario_real - precio_unitario_presupuesto) / precio_unitario_presupuesto) * 100
                ELSE 0 
            END
        ) PERSISTED,
        
        -- Specifications for this work
        especificaciones_obra NTEXT, -- Especificaciones específicas para esta obra
        medidas_especiales NVARCHAR(200), -- Medidas específicas
        color_obra NVARCHAR(50), -- Color específico para esta obra
        acabado_obra NVARCHAR(50), -- Acabado específico
        
        -- Quality & Compliance
        requiere_inspeccion BIT DEFAULT 0,
        inspeccion_realizada BIT DEFAULT 0,
        fecha_inspeccion DATETIME,
        resultado_inspeccion NVARCHAR(100),
        certificacion_obra NVARCHAR(100),
        
        -- Installation & Labor
        requiere_instalacion BIT DEFAULT 0,
        tiempo_instalacion_estimado DECIMAL(5,2), -- Horas estimadas
        tiempo_instalacion_real DECIMAL(5,2), -- Horas reales
        responsable_instalacion NVARCHAR(100),
        cuadrilla_asignada NVARCHAR(100),
        
        -- Logistics & Transport
        requiere_transporte_especial BIT DEFAULT 0,
        instrucciones_transporte NTEXT,
        peso_total AS (cantidad_requerida * 
            (SELECT peso FROM productos p WHERE p.id = producto_id)
        ) PERSISTED,
        volumen_estimado DECIMAL(10,3),
        
        -- Supplier & Procurement
        proveedor_asignado NVARCHAR(100),
        tiempo_entrega_estimado INT, -- Días
        numero_orden_compra NVARCHAR(100),
        fecha_pedido_proveedor DATE,
        
        -- Waste & Efficiency
        porcentaje_desperdicio DECIMAL(5,2) DEFAULT 5, -- % de desperdicio estimado
        cantidad_desperdicio AS (cantidad_requerida * (porcentaje_desperdicio / 100)) PERSISTED,
        cantidad_total_pedido AS (cantidad_requerida * (1 + porcentaje_desperdicio / 100)) PERSISTED,
        
        -- Additional Information
        observaciones NTEXT,
        notas_tecnicas NTEXT,
        problemas_identificados NTEXT,
        soluciones_aplicadas NTEXT,
        
        -- Document Management
        plano_referencia NVARCHAR(255), -- Referencia al plano
        foto_instalacion NVARCHAR(255), -- Path a foto de la instalación
        documento_certificacion NVARCHAR(255), -- Path al certificado
        
        -- Approval Workflow
        requiere_aprobacion BIT DEFAULT 0,
        aprobado_por INT, -- Usuario que aprobó
        fecha_aprobacion DATETIME,
        comentarios_aprobacion NTEXT,
        
        -- Tracking & Audit
        usuario_asignacion INT, -- Quien hizo la asignación
        usuario_responsable INT, -- Responsable del seguimiento
        fecha_ultima_actualizacion DATETIME DEFAULT GETDATE(),
        
        -- Integration & ERP
        sincronizado_erp BIT DEFAULT 0,
        id_erp_externo NVARCHAR(100),
        fecha_sincronizacion DATETIME,
        
        -- Control Fields
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE(),
        usuario_creacion INT,
        usuario_modificacion INT,
        
        -- Version Control
        version INT DEFAULT 1,
        motivo_cambio NVARCHAR(255), -- Por qué se modificó
        
        -- Constraints
        CONSTRAINT CK_productos_obra_cantidades CHECK (cantidad_asignada <= cantidad_requerida + cantidad_desperdicio),
        CONSTRAINT CK_productos_obra_utilizadas CHECK (cantidad_utilizada <= cantidad_asignada),
        CONSTRAINT CK_productos_obra_fechas CHECK (fecha_asignacion <= fecha_entrega_obra OR fecha_entrega_obra IS NULL)
    );
    
    PRINT 'Tabla productos_obra creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos_obra ya existe - verificando estructura';
    
    -- Verificar y agregar columnas faltantes si es necesario
    IF COL_LENGTH('productos_obra', 'version') IS NULL
        ALTER TABLE productos_obra ADD version INT DEFAULT 1;
    
    IF COL_LENGTH('productos_obra', 'motivo_cambio') IS NULL
        ALTER TABLE productos_obra ADD motivo_cambio NVARCHAR(255);
END
GO

-- ==============================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- ==============================================

PRINT 'Creando índices de optimización...';

-- Índice principal por obra y producto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_obra_producto')
    CREATE INDEX IX_productos_obra_obra_producto ON productos_obra(obra_id, producto_id);
GO

-- Índice por estado y fecha
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_estado_fecha')
    CREATE INDEX IX_productos_obra_estado_fecha ON productos_obra(estado, fecha_requerida);
GO

-- Índice por categoría de producto
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_categoria')
    CREATE INDEX IX_productos_obra_categoria ON productos_obra(categoria_producto, obra_id);
GO

-- Índice por etapa de obra
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_etapa')
    CREATE INDEX IX_productos_obra_etapa ON productos_obra(etapa_obra, fecha_requerida);
GO

-- Índice por prioridad y estado
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_prioridad')
    CREATE INDEX IX_productos_obra_prioridad ON productos_obra(prioridad, estado)
    WHERE prioridad IN ('ALTA', 'CRITICA');
GO

-- Índice por asignación pendiente
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_obra_pendientes')
    CREATE INDEX IX_productos_obra_pendientes ON productos_obra(obra_id, estado, fecha_requerida)
    WHERE estado IN ('PLANIFICADO', 'SOLICITADO', 'APROBADO');
GO

-- ==============================================
-- CREAR VISTAS ESPECIALIZADAS
-- ==============================================

PRINT 'Creando vistas especializadas...';

-- Vista para productos pendientes por obra
IF OBJECT_ID('v_productos_obra_pendientes', 'V') IS NOT NULL
    DROP VIEW v_productos_obra_pendientes;
GO

CREATE VIEW v_productos_obra_pendientes AS
SELECT 
    po.obra_id,
    po.id,
    po.codigo_producto,
    po.descripcion_producto,
    po.categoria_producto,
    po.cantidad_requerida,
    po.cantidad_pendiente,
    po.fecha_requerida,
    po.estado,
    po.prioridad,
    po.etapa_obra,
    po.costo_total_presupuestado,
    CASE 
        WHEN po.fecha_requerida < GETDATE() AND po.estado NOT IN ('COMPLETADO', 'CANCELADO') THEN 'ATRASADO'
        WHEN po.fecha_requerida <= DATEADD(DAY, 7, GETDATE()) THEN 'URGENTE'
        WHEN po.fecha_requerida <= DATEADD(DAY, 30, GETDATE()) THEN 'PROXIMO'
        ELSE 'PLANIFICADO'
    END as urgencia,
    DATEDIFF(DAY, GETDATE(), po.fecha_requerida) as dias_para_entrega
FROM productos_obra po
WHERE po.activo = 1 
    AND po.estado NOT IN ('COMPLETADO', 'CANCELADO')
    AND po.cantidad_pendiente > 0;
GO

-- Vista para análisis de costos por obra
IF OBJECT_ID('v_productos_obra_costos', 'V') IS NOT NULL
    DROP VIEW v_productos_obra_costos;
GO

CREATE VIEW v_productos_obra_costos AS
SELECT 
    po.obra_id,
    po.categoria_producto,
    COUNT(*) as total_productos,
    SUM(po.cantidad_requerida) as cantidad_total_requerida,
    SUM(po.cantidad_asignada) as cantidad_total_asignada,
    SUM(po.cantidad_utilizada) as cantidad_total_utilizada,
    SUM(po.costo_total_presupuestado) as presupuesto_total,
    SUM(po.costo_total_real) as costo_real_total,
    SUM(po.costo_total_real - po.costo_total_presupuestado) as variacion_total,
    CASE 
        WHEN SUM(po.costo_total_presupuestado) > 0 THEN 
            (SUM(po.costo_total_real - po.costo_total_presupuestado) / SUM(po.costo_total_presupuestado)) * 100
        ELSE 0 
    END as porcentaje_variacion,
    AVG(po.variacion_presupuesto) as variacion_promedio
FROM productos_obra po
WHERE po.activo = 1
GROUP BY po.obra_id, po.categoria_producto;
GO

-- Vista para dashboard de obras
IF OBJECT_ID('v_dashboard_productos_obra', 'V') IS NOT NULL
    DROP VIEW v_dashboard_productos_obra;
GO

CREATE VIEW v_dashboard_productos_obra AS
SELECT 
    po.obra_id,
    COUNT(*) as total_productos,
    COUNT(CASE WHEN po.estado = 'COMPLETADO' THEN 1 END) as completados,
    COUNT(CASE WHEN po.estado IN ('PLANIFICADO', 'SOLICITADO') THEN 1 END) as pendientes,
    COUNT(CASE WHEN po.estado = 'ASIGNADO' THEN 1 END) as asignados,
    COUNT(CASE WHEN po.fecha_requerida < GETDATE() AND po.estado NOT IN ('COMPLETADO', 'CANCELADO') THEN 1 END) as atrasados,
    COUNT(CASE WHEN po.prioridad IN ('ALTA', 'CRITICA') THEN 1 END) as criticos,
    CAST(SUM(po.costo_total_presupuestado) AS DECIMAL(18,2)) as presupuesto_total,
    CAST(SUM(po.costo_total_real) AS DECIMAL(18,2)) as costo_real_total,
    CAST(AVG(po.porcentaje_desperdicio) AS DECIMAL(5,2)) as desperdicio_promedio,
    COUNT(CASE WHEN po.requiere_instalacion = 1 THEN 1 END) as requieren_instalacion,
    COUNT(CASE WHEN po.requiere_inspeccion = 1 THEN 1 END) as requieren_inspeccion
FROM productos_obra po
WHERE po.activo = 1
GROUP BY po.obra_id;
GO

-- Vista para control de inventario por obra
IF OBJECT_ID('v_inventario_por_obra', 'V') IS NOT NULL
    DROP VIEW v_inventario_por_obra;
GO

CREATE VIEW v_inventario_por_obra AS
SELECT 
    po.obra_id,
    po.producto_id,
    p.codigo as codigo_producto,
    p.descripcion as descripcion_producto,
    p.categoria,
    p.stock_actual as stock_disponible,
    SUM(po.cantidad_requerida) as total_requerido_obra,
    SUM(po.cantidad_asignada) as total_asignado_obra,
    SUM(po.cantidad_pendiente) as total_pendiente_obra,
    p.stock_actual - SUM(po.cantidad_pendiente) as stock_libre,
    CASE 
        WHEN p.stock_actual < SUM(po.cantidad_pendiente) THEN 'INSUFICIENTE'
        WHEN p.stock_actual < SUM(po.cantidad_pendiente) * 1.1 THEN 'JUSTO'
        ELSE 'SUFICIENTE'
    END as disponibilidad_stock,
    MIN(po.fecha_requerida) as primera_fecha_necesaria
FROM productos_obra po
INNER JOIN productos p ON po.producto_id = p.id
WHERE po.activo = 1 AND po.estado NOT IN ('COMPLETADO', 'CANCELADO')
GROUP BY po.obra_id, po.producto_id, p.codigo, p.descripcion, p.categoria, p.stock_actual;
GO

PRINT '';
PRINT '=== TABLA PRODUCTOS_OBRA UNIFICADA CREADA EXITOSAMENTE ===';
PRINT 'Tabla creada: 1';
PRINT 'Índices creados: 6';
PRINT 'Vistas creadas: 4';
PRINT '';
PRINT 'Características principales:';
PRINT '- Asignación unificada de productos a obras';
PRINT '- Control detallado de cantidades y estados';
PRINT '- Seguimiento de costos vs presupuesto';
PRINT '- Gestión de etapas y ubicaciones en obra';
PRINT '- Control de calidad e inspecciones';
PRINT '- Análisis de desperdicios y eficiencia';
PRINT '- Dashboard integrado para seguimiento';
PRINT '';
PRINT 'Próximo paso: Ejecutar 10_migrar_asignaciones_obra.sql';
GO