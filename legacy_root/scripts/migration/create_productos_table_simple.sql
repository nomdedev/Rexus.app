-- =====================================================
-- CREAR TABLA PRODUCTOS CONSOLIDADA - VERSION SIMPLIFICADA
-- Reemplaza: inventario_perfiles, herrajes, vidrios, materiales
-- =====================================================

USE inventario;
GO

-- Eliminar tabla si existe (para recrear limpia)
IF OBJECT_ID('productos', 'U') IS NOT NULL
BEGIN
    DROP TABLE productos;
    PRINT 'Tabla productos existente eliminada';
END
GO

-- Crear tabla productos consolidada
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(50) UNIQUE NOT NULL,
    descripcion NVARCHAR(255) NOT NULL,
    
    -- Categorización
    categoria NVARCHAR(50) NOT NULL CHECK (categoria IN ('PERFIL', 'HERRAJE', 'VIDRIO', 'MATERIAL')),
    subcategoria NVARCHAR(50),
    tipo NVARCHAR(100),
    
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
    color NVARCHAR(50),
    material NVARCHAR(50),
    marca NVARCHAR(50),
    modelo NVARCHAR(50),
    acabado NVARCHAR(50),
    
    -- Supplier Info
    proveedor NVARCHAR(100),
    codigo_proveedor NVARCHAR(50),
    tiempo_entrega_dias INT DEFAULT 0,
    
    -- Additional Properties (JSON for category-specific data)
    propiedades_especiales NVARCHAR(MAX), -- JSON for vidrios: espesor, templado, laminado, etc.
    observaciones NVARCHAR(MAX),
    
    -- QR & Images
    codigo_qr NVARCHAR(255),
    imagen_url NVARCHAR(255),
    
    -- Control Fields
    estado NVARCHAR(20) DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'INACTIVO', 'DESCONTINUADO')),
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    usuario_creacion NVARCHAR(50),
    usuario_modificacion NVARCHAR(50)
);

PRINT 'Tabla productos creada exitosamente';
GO

-- Crear índices para optimización
CREATE INDEX IX_productos_categoria_estado ON productos(categoria, estado);
CREATE INDEX IX_productos_codigo ON productos(codigo);
CREATE INDEX IX_productos_descripcion ON productos(descripcion);
CREATE INDEX IX_productos_stock_critico ON productos(stock_actual, stock_minimo);
CREATE INDEX IX_productos_proveedor ON productos(proveedor);

PRINT 'Índices creados exitosamente';
GO

-- Crear trigger para actualizar fecha_actualizacion
CREATE TRIGGER TR_productos_update_timestamp
ON productos
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE productos
    SET fecha_actualizacion = GETDATE()
    FROM productos
    INNER JOIN inserted i ON productos.id = i.id;
END
GO

-- Crear vista para productos con stock bajo
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

-- Crear procedimiento para buscar productos
CREATE PROCEDURE sp_buscar_productos_consolidado
    @busqueda NVARCHAR(255) = NULL,
    @categoria NVARCHAR(50) = NULL,
    @estado NVARCHAR(20) = 'ACTIVO',
    @solo_stock_bajo BIT = 0,
    @proveedor NVARCHAR(100) = NULL,
    @limite INT = 100
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TOP (@limite)
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
        descripcion;
END
GO

PRINT '=== TABLA PRODUCTOS CREADA EXITOSAMENTE ===';
PRINT 'Índices creados: 5';
PRINT 'Triggers creados: 1';
PRINT 'Vistas creadas: 1';
PRINT 'Procedimientos creados: 1';
PRINT '';
PRINT 'La tabla productos está lista para migración de datos';
GO