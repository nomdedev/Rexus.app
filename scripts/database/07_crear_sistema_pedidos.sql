-- =====================================================
-- FASE 2.1: Crear Sistema Consolidado de Pedidos
-- Reemplaza: pedidos, pedidos_compra, compras y sus detalles
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO FASE 2: Sistema Consolidado de Pedidos ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- ==============================================
-- CREAR TABLA PEDIDOS CONSOLIDADA
-- ==============================================

IF OBJECT_ID('pedidos_consolidado', 'U') IS NULL
BEGIN
    CREATE TABLE pedidos_consolidado (
        id INT IDENTITY(1,1) PRIMARY KEY,
        numero_pedido NVARCHAR(50) UNIQUE NOT NULL,
        
        -- Relationship
        obra_id INT, -- FOREIGN KEY REFERENCES obras(id) - se agregará después
        cliente_id INT, -- Para futuro sistema de clientes
        proveedor_id INT, -- Para sistema de proveedores
        
        -- Order Classification
        tipo_pedido NVARCHAR(50) NOT NULL CHECK (tipo_pedido IN ('COMPRA', 'VENTA', 'INTERNO', 'OBRA', 'TRANSFERENCIA')),
        categoria_pedido NVARCHAR(50) CHECK (categoria_pedido IN ('MATERIAL', 'HERRAJE', 'VIDRIO', 'MIXTO', 'SERVICIO')),
        origen_pedido NVARCHAR(50) DEFAULT 'MANUAL' CHECK (origen_pedido IN ('MANUAL', 'AUTOMATICO', 'IMPORTADO', 'API')),
        
        -- Status Management
        estado NVARCHAR(50) DEFAULT 'BORRADOR' CHECK (estado IN (
            'BORRADOR', 'PENDIENTE', 'APROBADO', 'EN_PROCESO', 'PARCIALMENTE_ENTREGADO', 
            'ENTREGADO', 'FACTURADO', 'CANCELADO', 'RECHAZADO'
        )),
        estado_anterior NVARCHAR(50), -- Para auditoría de cambios de estado
        prioridad NVARCHAR(20) DEFAULT 'NORMAL' CHECK (prioridad IN ('BAJA', 'NORMAL', 'ALTA', 'URGENTE')),
        
        -- Dates & Timeline
        fecha_pedido DATETIME DEFAULT GETDATE() NOT NULL,
        fecha_necesaria DATE, -- Cuándo se necesita
        fecha_entrega_solicitada DATE,
        fecha_entrega_prometida DATE,
        fecha_entrega_real DATE,
        fecha_aprobacion DATETIME,
        fecha_cancelacion DATETIME,
        
        -- Financial Information
        moneda NVARCHAR(3) DEFAULT 'ARS',
        subtotal DECIMAL(18,2) DEFAULT 0 CHECK (subtotal >= 0),
        descuento_porcentaje DECIMAL(5,2) DEFAULT 0 CHECK (descuento_porcentaje >= 0 AND descuento_porcentaje <= 100),
        descuento_monto DECIMAL(18,2) DEFAULT 0 CHECK (descuento_monto >= 0),
        impuestos_porcentaje DECIMAL(5,2) DEFAULT 21, -- IVA por defecto en Argentina
        impuestos_monto DECIMAL(18,2) DEFAULT 0 CHECK (impuestos_monto >= 0),
        otros_cargos DECIMAL(18,2) DEFAULT 0,
        total DECIMAL(18,2) DEFAULT 0 CHECK (total >= 0),
        
        -- Delivery & Logistics
        direccion_entrega NTEXT,
        contacto_entrega NVARCHAR(100),
        telefono_contacto NVARCHAR(50),
        instrucciones_entrega NTEXT,
        metodo_envio NVARCHAR(50),
        costo_envio DECIMAL(18,2) DEFAULT 0,
        
        -- Business Context
        referencia_externa NVARCHAR(100), -- Número de orden del cliente/proveedor
        orden_compra_cliente NVARCHAR(100),
        numero_presupuesto NVARCHAR(100),
        condiciones_pago NVARCHAR(100) DEFAULT '30 días',
        
        -- Approval Workflow
        requiere_aprobacion BIT DEFAULT 0,
        usuario_creador INT NOT NULL,
        usuario_aprobador INT,
        usuario_responsable INT, -- Quien gestiona el pedido
        departamento_solicitante NVARCHAR(100),
        
        -- Additional Information
        observaciones NTEXT,
        observaciones_internas NTEXT, -- No visible para clientes/proveedores
        motivo_cancelacion NTEXT,
        archivo_adjunto NVARCHAR(255), -- Path al archivo
        
        -- Tracking & Analytics
        origen_cotizacion NVARCHAR(100), -- De qué cotización viene
        campana_marketing NVARCHAR(100), -- Para análisis de marketing
        canal_venta NVARCHAR(50), -- WEB, TELEFONO, PRESENCIAL, etc.
        
        -- Integration Fields
        sincronizado_erp BIT DEFAULT 0,
        id_erp_externo NVARCHAR(100),
        fecha_sincronizacion DATETIME,
        
        -- Control Fields
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE(),
        usuario_modificacion INT,
        
        -- Version Control
        version INT DEFAULT 1,
        bloqueado_edicion BIT DEFAULT 0, -- Para evitar edición concurrente
        usuario_bloqueo INT,
        fecha_bloqueo DATETIME
    );
    
    PRINT 'Tabla pedidos_consolidado creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla pedidos_consolidado ya existe';
END
GO

-- ==============================================
-- CREAR TABLA PEDIDOS_DETALLE CONSOLIDADA
-- ==============================================

IF OBJECT_ID('pedidos_detalle_consolidado', 'U') IS NULL
BEGIN
    CREATE TABLE pedidos_detalle_consolidado (
        id INT IDENTITY(1,1) PRIMARY KEY,
        pedido_id INT NOT NULL, -- FOREIGN KEY REFERENCES pedidos_consolidado(id)
        
        -- Product Reference (usando tabla productos consolidada)
        producto_id INT NOT NULL, -- FOREIGN KEY REFERENCES productos(id)
        
        -- Product Snapshot (para auditoría y cambios de precios)
        codigo_producto NVARCHAR(50) NOT NULL, -- Snapshot al momento del pedido
        descripcion_producto NVARCHAR(255) NOT NULL,
        categoria_producto NVARCHAR(50),
        
        -- Quantities & Units
        cantidad DECIMAL(10,3) NOT NULL CHECK (cantidad > 0),
        cantidad_entregada DECIMAL(10,3) DEFAULT 0 CHECK (cantidad_entregada >= 0),
        cantidad_pendiente AS (cantidad - cantidad_entregada) PERSISTED,
        cantidad_facturada DECIMAL(10,3) DEFAULT 0 CHECK (cantidad_facturada >= 0),
        
        unidad_medida NVARCHAR(20) NOT NULL DEFAULT 'UND',
        factor_conversion DECIMAL(10,6) DEFAULT 1, -- Para conversiones de unidades
        
        -- Pricing & Costs
        precio_unitario DECIMAL(18,2) NOT NULL CHECK (precio_unitario >= 0),
        precio_original DECIMAL(18,2), -- Precio antes de descuentos
        descuento_porcentaje DECIMAL(5,2) DEFAULT 0 CHECK (descuento_porcentaje >= 0 AND descuento_porcentaje <= 100),
        descuento_monto DECIMAL(18,2) DEFAULT 0 CHECK (descuento_monto >= 0),
        subtotal_item DECIMAL(18,2) NOT NULL CHECK (subtotal_item >= 0),
        
        -- Cost Analysis
        costo_unitario DECIMAL(18,2) DEFAULT 0, -- Para análisis de rentabilidad
        margen_beneficio AS (
            CASE 
                WHEN costo_unitario > 0 THEN ((precio_unitario - costo_unitario) / precio_unitario) * 100
                ELSE 0 
            END
        ) PERSISTED,
        
        -- Delivery Planning
        fecha_entrega_solicitada DATE,
        fecha_entrega_prometida DATE,
        fecha_entrega_real DATE,
        
        -- Item Status
        estado_item NVARCHAR(50) DEFAULT 'PENDIENTE' CHECK (estado_item IN (
            'PENDIENTE', 'CONFIRMADO', 'EN_PRODUCCION', 'LISTO', 'ENVIADO', 'ENTREGADO', 'CANCELADO'
        )),
        
        -- Specifications & Customization
        especificaciones_item NTEXT, -- Especificaciones particulares del ítem
        personalizacion NTEXT, -- Datos de personalización
        medidas_especiales NVARCHAR(200), -- Medidas específicas para este pedido
        color_especial NVARCHAR(50),
        acabado_especial NVARCHAR(50),
        
        -- Quality & Compliance
        requiere_inspeccion BIT DEFAULT 0,
        certificacion_requerida NVARCHAR(100),
        normas_aplicables NVARCHAR(200),
        
        -- Logistics
        peso_item DECIMAL(10,3),
        volumen_item DECIMAL(10,3),
        requiere_instalacion BIT DEFAULT 0,
        instrucciones_instalacion NTEXT,
        
        -- Business Rules
        es_item_critico BIT DEFAULT 0,
        permite_entregas_parciales BIT DEFAULT 1,
        requiere_aprobacion_cambios BIT DEFAULT 0,
        
        -- Inventory Impact
        reserva_stock BIT DEFAULT 1, -- Si debe reservar stock al confirmar
        stock_reservado DECIMAL(10,3) DEFAULT 0,
        fecha_reserva DATETIME,
        
        -- Additional Information
        observaciones_item NTEXT,
        notas_produccion NTEXT,
        referencia_cliente NVARCHAR(100), -- Referencia del cliente para este ítem
        
        -- Control Fields
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE(),
        usuario_modificacion INT,
        
        -- Line Number for ordering
        numero_linea INT DEFAULT 0,
        grupo_items NVARCHAR(50), -- Para agrupar ítems relacionados
        
        -- Integration
        sincronizado_erp BIT DEFAULT 0,
        id_erp_externo NVARCHAR(100)
    );
    
    PRINT 'Tabla pedidos_detalle_consolidado creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla pedidos_detalle_consolidado ya existe';
END
GO

-- ==============================================
-- CREAR ÍNDICES PARA OPTIMIZACIÓN
-- ==============================================

PRINT 'Creando índices de optimización...';

-- Índices para pedidos_consolidado
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_numero')
    CREATE UNIQUE INDEX IX_pedidos_numero ON pedidos_consolidado(numero_pedido);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_estado_fecha')
    CREATE INDEX IX_pedidos_estado_fecha ON pedidos_consolidado(estado, fecha_pedido DESC);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_tipo_categoria')
    CREATE INDEX IX_pedidos_tipo_categoria ON pedidos_consolidado(tipo_pedido, categoria_pedido);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_obra_id')
    CREATE INDEX IX_pedidos_obra_id ON pedidos_consolidado(obra_id)
    WHERE obra_id IS NOT NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_usuario_creador')
    CREATE INDEX IX_pedidos_usuario_creador ON pedidos_consolidado(usuario_creador, fecha_creacion DESC);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pedidos_fecha_entrega')
    CREATE INDEX IX_pedidos_fecha_entrega ON pedidos_consolidado(fecha_entrega_solicitada, estado)
    WHERE fecha_entrega_solicitada IS NOT NULL;
GO

-- Índices para pedidos_detalle_consolidado
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_detalle_pedido_id')
    CREATE INDEX IX_detalle_pedido_id ON pedidos_detalle_consolidado(pedido_id);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_detalle_producto_id')
    CREATE INDEX IX_detalle_producto_id ON pedidos_detalle_consolidado(producto_id);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_detalle_estado_fecha')
    CREATE INDEX IX_detalle_estado_fecha ON pedidos_detalle_consolidado(estado_item, fecha_entrega_solicitada);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_detalle_codigo_producto')
    CREATE INDEX IX_detalle_codigo_producto ON pedidos_detalle_consolidado(codigo_producto);
GO

-- ==============================================
-- CREAR VISTAS ESPECIALIZADAS
-- ==============================================

PRINT 'Creando vistas especializadas...';

-- Vista para pedidos pendientes
IF OBJECT_ID('v_pedidos_pendientes', 'V') IS NOT NULL
    DROP VIEW v_pedidos_pendientes;
GO

CREATE VIEW v_pedidos_pendientes AS
SELECT 
    p.id, p.numero_pedido, p.tipo_pedido, p.categoria_pedido,
    p.estado, p.prioridad, p.fecha_pedido, p.fecha_entrega_solicitada,
    p.total, p.moneda, p.usuario_creador,
    COUNT(d.id) as total_items,
    SUM(d.cantidad) as total_cantidad,
    SUM(d.cantidad_pendiente) as cantidad_pendiente,
    CASE 
        WHEN SUM(d.cantidad_pendiente) = 0 THEN 'COMPLETO'
        WHEN SUM(d.cantidad_entregada) > 0 THEN 'PARCIAL'
        ELSE 'PENDIENTE'
    END as estado_entrega
FROM pedidos_consolidado p
LEFT JOIN pedidos_detalle_consolidado d ON p.id = d.pedido_id AND d.activo = 1
WHERE p.estado IN ('APROBADO', 'EN_PROCESO', 'PARCIALMENTE_ENTREGADO')
    AND p.activo = 1
GROUP BY p.id, p.numero_pedido, p.tipo_pedido, p.categoria_pedido,
         p.estado, p.prioridad, p.fecha_pedido, p.fecha_entrega_solicitada,
         p.total, p.moneda, p.usuario_creador;
GO

-- Vista para análisis de rentabilidad
IF OBJECT_ID('v_pedidos_rentabilidad', 'V') IS NOT NULL
    DROP VIEW v_pedidos_rentabilidad;
GO

CREATE VIEW v_pedidos_rentabilidad AS
SELECT 
    p.id, p.numero_pedido, p.tipo_pedido, p.fecha_pedido,
    p.subtotal, p.total,
    SUM(d.cantidad * d.costo_unitario) as costo_total,
    p.total - SUM(d.cantidad * d.costo_unitario) as ganancia_bruta,
    CASE 
        WHEN p.total > 0 THEN 
            ((p.total - SUM(d.cantidad * d.costo_unitario)) / p.total) * 100
        ELSE 0 
    END as margen_porcentaje,
    AVG(d.margen_beneficio) as margen_promedio_items
FROM pedidos_consolidado p
INNER JOIN pedidos_detalle_consolidado d ON p.id = d.pedido_id
WHERE p.activo = 1 AND d.activo = 1 AND p.estado NOT IN ('BORRADOR', 'CANCELADO')
GROUP BY p.id, p.numero_pedido, p.tipo_pedido, p.fecha_pedido, p.subtotal, p.total;
GO

-- Vista para dashboard de pedidos
IF OBJECT_ID('v_dashboard_pedidos', 'V') IS NOT NULL
    DROP VIEW v_dashboard_pedidos;
GO

CREATE VIEW v_dashboard_pedidos AS
SELECT 
    COUNT(*) as total_pedidos,
    SUM(CASE WHEN estado = 'BORRADOR' THEN 1 ELSE 0 END) as borradores,
    SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as pendientes,
    SUM(CASE WHEN estado = 'APROBADO' THEN 1 ELSE 0 END) as aprobados,
    SUM(CASE WHEN estado = 'EN_PROCESO' THEN 1 ELSE 0 END) as en_proceso,
    SUM(CASE WHEN estado = 'ENTREGADO' THEN 1 ELSE 0 END) as entregados,
    SUM(CASE WHEN estado = 'CANCELADO' THEN 1 ELSE 0 END) as cancelados,
    SUM(CASE WHEN prioridad = 'URGENTE' THEN 1 ELSE 0 END) as urgentes,
    CAST(SUM(total) AS DECIMAL(18,2)) as valor_total,
    CAST(AVG(total) AS DECIMAL(18,2)) as valor_promedio,
    COUNT(CASE WHEN fecha_entrega_solicitada < GETDATE() AND estado NOT IN ('ENTREGADO', 'CANCELADO') THEN 1 END) as atrasados
FROM pedidos_consolidado
WHERE activo = 1 AND fecha_pedido >= DATEADD(MONTH, -3, GETDATE()); -- Últimos 3 meses
GO

PRINT '';
PRINT '=== SISTEMA DE PEDIDOS CONSOLIDADO CREADO EXITOSAMENTE ===';
PRINT 'Tablas creadas: 2';
PRINT 'Índices creados: 10';
PRINT 'Vistas creadas: 3';
PRINT '';
PRINT 'Características principales:';
PRINT '- Soporte para múltiples tipos de pedidos (COMPRA, VENTA, OBRA, etc.)';
PRINT '- Workflow de aprobación integrado';
PRINT '- Seguimiento detallado de entregas';
PRINT '- Análisis de rentabilidad por ítem';
PRINT '- Gestión de especificaciones personalizadas';
PRINT '- Integración con sistema de productos consolidado';
PRINT '';
PRINT 'Próximo paso: Ejecutar 08_migrar_pedidos_existentes.sql';
GO