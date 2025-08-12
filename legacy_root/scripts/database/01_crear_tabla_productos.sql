-- =====================================================
-- FASE 1.1: Crear Tabla Consolidada 'productos'
-- Reemplaza: inventario_perfiles, herrajes, vidrios, materiales
-- =====================================================

USE inventario;
GO

-- Crear tabla productos consolidada
IF OBJECT_ID('productos', 'U') IS NULL
BEGIN
    CREATE TABLE productos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo NVARCHAR(50) UNIQUE NOT NULL,
        descripcion NVARCHAR(255) NOT NULL,
        
        -- Categorización
        categoria NVARCHAR(50) NOT NULL CHECK (categoria IN ('PERFIL', 'HERRAJE', 'VIDRIO', 'MATERIAL')),
        subcategoria NVARCHAR(50), -- tipo, acabado, etc.
        tipo NVARCHAR(100), -- tipo específico del producto
        
        -- Stock Management
        stock_actual DECIMAL(18,2) DEFAULT 0 CHECK (stock_actual >= 0),
        stock_minimo DECIMAL(18,2) DEFAULT 0 CHECK (stock_minimo >= 0),
        stock_maximo DECIMAL(18,2) DEFAULT 1000 CHECK (stock_maximo >= stock_minimo),
        stock_reservado DECIMAL(18,2) DEFAULT 0 CHECK (stock_reservado >= 0),
        stock_disponible AS (stock_actual - stock_reservado) PERSISTED,
        
        -- Pricing
        precio_unitario DECIMAL(18,2) DEFAULT 0 CHECK (precio_unitario >= 0),
        precio_promedio DECIMAL(18,2) DEFAULT 0 CHECK (precio_promedio >= 0),
        costo_unitario DECIMAL(18,2) DEFAULT 0 CHECK (costo_unitario >= 0),
        
        -- Physical Properties
        unidad_medida NVARCHAR(20) DEFAULT 'UND',
        ubicacion NVARCHAR(100),
        dimensiones NVARCHAR(100), -- length x width x height
        peso DECIMAL(10,3),
        color NVARCHAR(50),
        material NVARCHAR(50),
        marca NVARCHAR(50),
        modelo NVARCHAR(50),
        acabado NVARCHAR(50),
        
        -- Supplier Info
        proveedor NVARCHAR(100),
        codigo_proveedor NVARCHAR(50),
        tiempo_entrega_dias INT DEFAULT 0,
        
        -- Additional Data (JSON for flexibility)
        propiedades_adicionales NTEXT, -- JSON for category-specific properties
        especificaciones NTEXT,
        observaciones NTEXT,
        ficha_tecnica NTEXT, -- Technical specifications
        
        -- QR & Images
        codigo_qr NVARCHAR(255),
        imagen_url NVARCHAR(255),
        codigo_barras NVARCHAR(100),
        
        -- Business Rules
        es_critico BIT DEFAULT 0, -- Critical for operations
        permite_reserva BIT DEFAULT 1, -- Can be reserved
        requiere_aprobacion BIT DEFAULT 0, -- Requires approval for orders
        
        -- Control Fields
        estado NVARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'DESCONTINUADO')),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_actualizacion DATETIME DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(50),
        usuario_modificacion NVARCHAR(50),
        
        -- Version Control
        version INT DEFAULT 1,
        fecha_ultima_compra DATETIME,
        fecha_ultimo_movimiento DATETIME
    );
    
    PRINT 'Tabla productos creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla productos ya existe';
END
GO

-- Crear índices para optimización
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_categoria_estado')
    CREATE INDEX IX_productos_categoria_estado ON productos(categoria, estado);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_codigo')
    CREATE INDEX IX_productos_codigo ON productos(codigo);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_descripcion')
    CREATE INDEX IX_productos_descripcion ON productos(descripcion);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_stock_critico')
    CREATE INDEX IX_productos_stock_critico ON productos(stock_actual, stock_minimo) 
    WHERE es_critico = 1;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_productos_proveedor')
    CREATE INDEX IX_productos_proveedor ON productos(proveedor);
GO

-- Crear trigger para actualizar fecha_actualizacion
IF OBJECT_ID('TR_productos_update_timestamp', 'TR') IS NOT NULL
    DROP TRIGGER TR_productos_update_timestamp;
GO

CREATE TRIGGER TR_productos_update_timestamp
ON productos
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE productos
    SET fecha_actualizacion = GETDATE(),
        fecha_ultimo_movimiento = CASE 
            WHEN i.stock_actual != d.stock_actual THEN GETDATE()
            ELSE productos.fecha_ultimo_movimiento
        END
    FROM productos
    INNER JOIN inserted i ON productos.id = i.id
    INNER JOIN deleted d ON productos.id = d.id;
END
GO

-- Crear vista para productos con stock bajo
IF OBJECT_ID('v_productos_stock_bajo', 'V') IS NOT NULL
    DROP VIEW v_productos_stock_bajo;
GO

CREATE VIEW v_productos_stock_bajo AS
SELECT 
    id, codigo, descripcion, categoria, subcategoria,
    stock_actual, stock_minimo, stock_disponible,
    (stock_minimo - stock_actual) as deficit_stock,
    proveedor, tiempo_entrega_dias,
    CASE 
        WHEN stock_actual = 0 THEN 'SIN_STOCK'
        WHEN stock_actual <= stock_minimo * 0.5 THEN 'CRITICO'
        WHEN stock_actual <= stock_minimo THEN 'BAJO'
        ELSE 'NORMAL'
    END as nivel_alerta
FROM productos
WHERE estado = 'ACTIVO' 
    AND stock_actual <= stock_minimo
    AND activo = 1;
GO

-- Crear vista para estadísticas por categoría
IF OBJECT_ID('v_estadisticas_productos', 'V') IS NOT NULL
    DROP VIEW v_estadisticas_productos;
GO

CREATE VIEW v_estadisticas_productos AS
SELECT 
    categoria,
    COUNT(*) as total_productos,
    SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
    SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as con_stock_bajo,
    SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as sin_stock,
    SUM(stock_actual * precio_unitario) as valor_inventario_categoria,
    AVG(stock_actual) as promedio_stock,
    MIN(fecha_creacion) as primer_producto,
    MAX(fecha_actualizacion) as ultima_actualizacion
FROM productos
WHERE activo = 1
GROUP BY categoria;
GO

-- Crear función para calcular valor total de inventario
IF OBJECT_ID('fn_valor_inventario_categoria', 'FN') IS NOT NULL
    DROP FUNCTION fn_valor_inventario_categoria;
GO

CREATE FUNCTION fn_valor_inventario_categoria(@categoria NVARCHAR(50) = NULL)
RETURNS DECIMAL(18,2)
AS
BEGIN
    DECLARE @valor DECIMAL(18,2);
    
    SELECT @valor = SUM(stock_actual * precio_unitario)
    FROM productos
    WHERE activo = 1
        AND estado = 'ACTIVO'
        AND (@categoria IS NULL OR categoria = @categoria);
    
    RETURN ISNULL(@valor, 0);
END
GO

-- Crear procedimiento para obtener productos con filtros
IF OBJECT_ID('sp_buscar_productos', 'P') IS NOT NULL
    DROP PROCEDURE sp_buscar_productos;
GO

CREATE PROCEDURE sp_buscar_productos
    @busqueda NVARCHAR(255) = NULL,
    @categoria NVARCHAR(50) = NULL,
    @estado NVARCHAR(20) = 'ACTIVO',
    @solo_stock_bajo BIT = 0,
    @proveedor NVARCHAR(100) = NULL,
    @limite INT = 100,
    @offset INT = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        id, codigo, descripcion, categoria, subcategoria, tipo,
        stock_actual, stock_minimo, stock_disponible,
        precio_unitario, unidad_medida, ubicacion,
        color, material, marca, modelo, proveedor,
        estado, fecha_actualizacion,
        CASE 
            WHEN stock_actual = 0 THEN 'SIN_STOCK'
            WHEN stock_actual <= stock_minimo * 0.5 THEN 'CRITICO'
            WHEN stock_actual <= stock_minimo THEN 'BAJO'
            ELSE 'NORMAL'
        END as nivel_stock
    FROM productos
    WHERE activo = 1
        AND (@estado IS NULL OR estado = @estado)
        AND (@categoria IS NULL OR categoria = @categoria)
        AND (@proveedor IS NULL OR proveedor LIKE '%' + @proveedor + '%')
        AND (@busqueda IS NULL OR 
             codigo LIKE '%' + @busqueda + '%' OR
             descripcion LIKE '%' + @busqueda + '%' OR
             marca LIKE '%' + @busqueda + '%' OR
             modelo LIKE '%' + @busqueda + '%')
        AND (@solo_stock_bajo = 0 OR stock_actual <= stock_minimo)
    ORDER BY 
        CASE WHEN stock_actual = 0 THEN 1 
             WHEN stock_actual <= stock_minimo THEN 2 
             ELSE 3 END,
        descripcion
    OFFSET @offset ROWS
    FETCH NEXT @limite ROWS ONLY;
END
GO

PRINT '=== TABLA PRODUCTOS CREADA EXITOSAMENTE ===';
PRINT 'Índices creados: 5';
PRINT 'Triggers creados: 1';
PRINT 'Vistas creadas: 2';
PRINT 'Funciones creadas: 1';
PRINT 'Procedimientos creados: 1';
PRINT '';
PRINT 'Próximo paso: Ejecutar script de migración de datos';
PRINT 'Archivo: 02_migrar_inventario_a_productos.sql';
GO