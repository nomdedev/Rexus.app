-- =====================================================================
-- CONSOLIDACIÓN DE TABLA PRODUCTOS - REXUS.APP (INVENTARIO + HERRAJES)
-- =====================================================================
-- Propósito: Unificar tablas de productos estándar (inventario, herrajes) 
--           en una sola tabla productos consolidada.
--           NOTA: Vidrios se mantienen separados por sus características únicas
--           (medidas exactas, espesores personalizados, cortes específicos)
-- Fecha: 2025-08-09
-- Versión: 1.1 (Ajustado sin vidrios)
-- =====================================================================

-- 1. CREAR TABLA PRODUCTOS CONSOLIDADA
-- =====================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos' AND xtype='U')
BEGIN
    CREATE TABLE productos (
        -- Campos básicos
        id int IDENTITY(1,1) PRIMARY KEY,
        codigo varchar(50) NOT NULL UNIQUE,
        nombre varchar(255) NOT NULL,
        descripcion text NULL,
        
        -- Categorización
        tipo_producto varchar(50) NOT NULL, -- 'INVENTARIO', 'HERRAJE', 'MATERIAL'
        categoria varchar(100) NULL,
        subcategoria varchar(100) NULL,
        
        -- Información económica
        precio_compra decimal(10,2) NULL DEFAULT 0.00,
        precio_venta decimal(10,2) NULL DEFAULT 0.00,
        margen_ganancia decimal(5,2) NULL DEFAULT 0.00,
        
        -- Control de inventario
        stock int NOT NULL DEFAULT 0,
        stock_minimo int NOT NULL DEFAULT 0,
        stock_maximo int NULL DEFAULT NULL,
        unidad_medida varchar(20) NOT NULL DEFAULT 'UNIDAD', -- 'UNIDAD', 'METRO', 'KG', 'LITRO', etc.
        
        -- Información del proveedor
        proveedor_id int NULL,
        proveedor_codigo varchar(50) NULL,
        codigo_barras varchar(50) NULL,
        
        -- Especificaciones técnicas (JSON para flexibilidad)
        especificaciones_tecnicas text NULL, -- JSON con specs específicas por tipo
        
        -- Campos específicos por tipo de producto
        -- Para herrajes
        tipo_herraje varchar(50) NULL,
        acabado varchar(50) NULL,
        material varchar(50) NULL,
        
        -- Para materiales generales
        densidad decimal(8,3) NULL,
        peso_unitario decimal(8,3) NULL,
        
        -- Control de calidad y estado
        estado varchar(20) NOT NULL DEFAULT 'ACTIVO', -- 'ACTIVO', 'INACTIVO', 'DESCONTINUADO'
        requiere_inspeccion bit DEFAULT 0,
        fecha_vencimiento datetime NULL,
        lote varchar(50) NULL,
        
        -- Ubicación física
        ubicacion_almacen varchar(100) NULL,
        pasillo varchar(20) NULL,
        estante varchar(20) NULL,
        
        -- Campos de auditoría
        activo bit NOT NULL DEFAULT 1,
        usuario_creacion varchar(100) NULL,
        fecha_creacion datetime NOT NULL DEFAULT GETDATE(),
        usuario_modificacion varchar(100) NULL,
        fecha_modificacion datetime NOT NULL DEFAULT GETDATE(),
        
        -- Campos de control de versión
        version int NOT NULL DEFAULT 1,
        fecha_ultima_revision datetime NULL
    );
    
    PRINT 'Tabla productos creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos ya existe';
END

-- =====================================================================
-- 2. CREAR ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================================

-- Índice único en código
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_codigo')
BEGIN
    CREATE UNIQUE INDEX IX_productos_codigo ON productos (codigo);
    PRINT 'Índice IX_productos_codigo creado';
END

-- Índice compuesto en tipo_producto y categoria
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_tipo_categoria')
BEGIN
    CREATE INDEX IX_productos_tipo_categoria ON productos (tipo_producto, categoria);
    PRINT 'Índice IX_productos_tipo_categoria creado';
END

-- Índice en estado y activo para consultas frecuentes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_estado_activo')
BEGIN
    CREATE INDEX IX_productos_estado_activo ON productos (estado, activo);
    PRINT 'Índice IX_productos_estado_activo creado';
END

-- Índice en stock para consultas de inventario
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_stock')
BEGIN
    CREATE INDEX IX_productos_stock ON productos (stock, stock_minimo);
    PRINT 'Índice IX_productos_stock creado';
END

-- Índice en proveedor_id
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_proveedor')
BEGIN
    CREATE INDEX IX_productos_proveedor ON productos (proveedor_id);
    PRINT 'Índice IX_productos_proveedor creado';
END

-- =====================================================================
-- 3. CREAR TABLA DE HISTORIAL DE PRODUCTOS
-- =====================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos_historial' AND xtype='U')
BEGIN
    CREATE TABLE productos_historial (
        id int IDENTITY(1,1) PRIMARY KEY,
        producto_id int NOT NULL,
        campo_modificado varchar(100) NOT NULL,
        valor_anterior text NULL,
        valor_nuevo text NULL,
        tipo_operacion varchar(20) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE', 'STOCK_CHANGE'
        motivo varchar(255) NULL,
        usuario varchar(100) NOT NULL,
        fecha_modificacion datetime NOT NULL DEFAULT GETDATE(),
        
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    
    PRINT 'Tabla productos_historial creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos_historial ya existe';
END

-- =====================================================================
-- 4. CREAR TABLA DE MOVIMIENTOS DE STOCK
-- =====================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos_movimientos' AND xtype='U')
BEGIN
    CREATE TABLE productos_movimientos (
        id int IDENTITY(1,1) PRIMARY KEY,
        producto_id int NOT NULL,
        tipo_movimiento varchar(20) NOT NULL, -- 'ENTRADA', 'SALIDA', 'AJUSTE', 'TRANSFERENCIA'
        cantidad int NOT NULL,
        stock_anterior int NOT NULL,
        stock_nuevo int NOT NULL,
        precio_unitario decimal(10,2) NULL,
        costo_total decimal(12,2) NULL,
        
        -- Referencia del movimiento
        documento_referencia varchar(100) NULL, -- Número de factura, orden, etc.
        obra_id int NULL, -- Si está relacionado con una obra
        usuario_id int NULL, -- Usuario que realizó el movimiento
        
        -- Detalles del movimiento
        motivo varchar(255) NULL,
        observaciones text NULL,
        
        -- Ubicación
        ubicacion_origen varchar(100) NULL,
        ubicacion_destino varchar(100) NULL,
        
        -- Auditoría
        usuario_creacion varchar(100) NOT NULL,
        fecha_creacion datetime NOT NULL DEFAULT GETDATE(),
        
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    );
    
    PRINT 'Tabla productos_movimientos creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos_movimientos ya existe';
END

-- =====================================================================
-- 5. CREAR TABLA DE PRODUCTOS POR OBRA (RELACIÓN MUCHOS A MUCHOS)
-- =====================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos_obras' AND xtype='U')
BEGIN
    CREATE TABLE productos_obras (
        id int IDENTITY(1,1) PRIMARY KEY,
        producto_id int NOT NULL,
        obra_id int NOT NULL,
        cantidad_requerida int NOT NULL DEFAULT 0,
        cantidad_asignada int NOT NULL DEFAULT 0,
        cantidad_utilizada int NOT NULL DEFAULT 0,
        cantidad_devuelta int NOT NULL DEFAULT 0,
        
        -- Precios específicos para la obra
        precio_unitario decimal(10,2) NULL,
        precio_total decimal(12,2) NULL,
        
        -- Estados y fechas
        estado varchar(20) NOT NULL DEFAULT 'PLANIFICADO', -- 'PLANIFICADO', 'ASIGNADO', 'EN_USO', 'COMPLETADO', 'CANCELADO'
        fecha_asignacion datetime NULL,
        fecha_inicio_uso datetime NULL,
        fecha_fin_uso datetime NULL,
        
        -- Observaciones y notas
        notas text NULL,
        prioridad varchar(10) DEFAULT 'MEDIA', -- 'ALTA', 'MEDIA', 'BAJA'
        
        -- Auditoría
        usuario_creacion varchar(100) NOT NULL,
        fecha_creacion datetime NOT NULL DEFAULT GETDATE(),
        usuario_modificacion varchar(100) NULL,
        fecha_modificacion datetime NOT NULL DEFAULT GETDATE(),
        activo bit NOT NULL DEFAULT 1,
        
        FOREIGN KEY (producto_id) REFERENCES productos(id),
        UNIQUE (producto_id, obra_id)
    );
    
    PRINT 'Tabla productos_obras creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos_obras ya existe';
END

-- =====================================================================
-- 6. CREAR VISTAS PARA COMPATIBILIDAD CON CÓDIGO EXISTENTE
-- =====================================================================

-- Vista para inventario (productos tipo INVENTARIO)
IF EXISTS (SELECT * FROM sys.views WHERE name = 'v_inventario')
    DROP VIEW v_inventario;

GO
CREATE VIEW v_inventario AS
SELECT 
    id,
    codigo,
    nombre,
    descripcion,
    categoria,
    precio_venta as precio,
    stock,
    stock_minimo,
    unidad_medida,
    estado,
    activo,
    fecha_creacion,
    fecha_modificacion
FROM productos 
WHERE tipo_producto = 'INVENTARIO' AND activo = 1;

GO
PRINT 'Vista v_inventario creada';

-- Vista para herrajes
IF EXISTS (SELECT * FROM sys.views WHERE name = 'v_herrajes')
    DROP VIEW v_herrajes;

GO
CREATE VIEW v_herrajes AS
SELECT 
    id,
    codigo,
    nombre,
    descripcion,
    categoria,
    precio_venta as precio,
    stock,
    stock_minimo,
    tipo_herraje,
    acabado,
    material,
    estado,
    activo,
    fecha_creacion,
    fecha_modificacion
FROM productos 
WHERE tipo_producto = 'HERRAJE' AND activo = 1;

GO
PRINT 'Vista v_herrajes creada';

-- NOTA: Los vidrios se mantienen en tabla separada por sus características únicas
-- No se crea vista v_vidrios ya que conservan su tabla original

-- =====================================================================
-- 7. INSERTAR DATOS DE EJEMPLO PARA TESTING
-- =====================================================================

-- Verificar si ya hay datos
IF NOT EXISTS (SELECT * FROM productos WHERE codigo = 'INV-001')
BEGIN
    INSERT INTO productos (
        codigo, nombre, descripcion, tipo_producto, categoria, 
        precio_compra, precio_venta, stock, stock_minimo, 
        unidad_medida, estado, usuario_creacion
    ) VALUES 
    ('INV-001', 'Martillo Profesional', 'Martillo de acero inoxidable para uso profesional', 'INVENTARIO', 'HERRAMIENTAS', 25.00, 35.00, 50, 10, 'UNIDAD', 'ACTIVO', 'SYSTEM'),
    ('HER-001', 'Bisagra Piano 2m', 'Bisagra piano de aluminio 2 metros', 'HERRAJE', 'BISAGRAS', 15.50, 22.00, 25, 5, 'UNIDAD', 'ACTIVO', 'SYSTEM'),
    ('MAT-001', 'Cemento Portland', 'Cemento Portland tipo I bolsa 50kg', 'MATERIAL', 'CEMENTOS', 12.00, 18.00, 100, 20, 'BOLSA', 'ACTIVO', 'SYSTEM');
    
    PRINT 'Datos de ejemplo insertados en productos';
END

-- =====================================================================
-- 8. CREAR TRIGGERS PARA AUDITORÍA AUTOMÁTICA
-- =====================================================================

-- Trigger para auditar cambios en productos
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_productos_audit')
    DROP TRIGGER tr_productos_audit;

GO
CREATE TRIGGER tr_productos_audit
ON productos
FOR UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Insertar registro de auditoría para cambios de stock
    IF UPDATE(stock)
    BEGIN
        INSERT INTO productos_historial (
            producto_id, campo_modificado, valor_anterior, valor_nuevo, 
            tipo_operacion, usuario, fecha_modificacion
        )
        SELECT 
            i.id, 'stock', CAST(d.stock AS varchar), CAST(i.stock AS varchar),
            'STOCK_CHANGE', ISNULL(i.usuario_modificacion, 'SYSTEM'), GETDATE()
        FROM inserted i
        INNER JOIN deleted d ON i.id = d.id
        WHERE i.stock != d.stock;
    END
    
    -- Actualizar fecha de modificación
    UPDATE productos 
    SET fecha_modificacion = GETDATE() 
    WHERE id IN (SELECT id FROM inserted);
END

GO
PRINT 'Trigger tr_productos_audit creado';

-- =====================================================================
-- 9. CREAR PROCEDIMIENTOS ALMACENADOS BÁSICOS
-- =====================================================================

-- Procedimiento para obtener productos con stock bajo
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_productos_stock_bajo')
    DROP PROCEDURE sp_productos_stock_bajo;

GO
CREATE PROCEDURE sp_productos_stock_bajo
AS
BEGIN
    SELECT 
        codigo,
        nombre,
        tipo_producto,
        categoria,
        stock,
        stock_minimo,
        (stock_minimo - stock) as deficit,
        precio_compra * (stock_minimo - stock) as costo_reposicion
    FROM productos 
    WHERE stock <= stock_minimo 
      AND activo = 1 
      AND estado = 'ACTIVO'
    ORDER BY (stock_minimo - stock) DESC;
END

GO
PRINT 'Procedimiento sp_productos_stock_bajo creado';

-- =====================================================================
-- 10. COMENTARIOS FINALES Y VERIFICACIÓN
-- =====================================================================

PRINT '========================================';
PRINT 'CONSOLIDACIÓN DE PRODUCTOS COMPLETADA';
PRINT '========================================';
PRINT 'Tablas creadas:';
PRINT '- productos (tabla principal)';
PRINT '- productos_historial (auditoría)';
PRINT '- productos_movimientos (stock)';  
PRINT '- productos_obras (relación con obras)';
PRINT '';
PRINT 'Vistas creadas:';
PRINT '- v_inventario (compatibilidad)';
PRINT '- v_herrajes (compatibilidad)';
PRINT '- v_vidrios (compatibilidad)';
PRINT '';
PRINT 'Procedimientos:';
PRINT '- sp_productos_stock_bajo';
PRINT '';
PRINT 'La consolidación está lista para migración de datos.';
PRINT '========================================';

-- Verificar la estructura creada
SELECT 
    'productos' as tabla,
    COUNT(*) as registros,
    MIN(fecha_creacion) as primera_creacion,
    MAX(fecha_modificacion) as ultima_modificacion
FROM productos
UNION ALL
SELECT 
    'productos_historial' as tabla,
    COUNT(*) as registros,
    MIN(fecha_modificacion) as primera_creacion,
    MAX(fecha_modificacion) as ultima_modificacion
FROM productos_historial
UNION ALL
SELECT 
    'productos_movimientos' as tabla,
    COUNT(*) as registros,
    MIN(fecha_creacion) as primera_creacion,
    MAX(fecha_creacion) as ultima_modificacion
FROM productos_movimientos
UNION ALL
SELECT 
    'productos_obras' as tabla,
    COUNT(*) as registros,
    MIN(fecha_creacion) as primera_creacion,
    MAX(fecha_modificacion) as ultima_modificacion
FROM productos_obras;