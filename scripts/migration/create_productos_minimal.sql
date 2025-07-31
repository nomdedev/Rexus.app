-- =====================================================
-- CREAR TABLA PRODUCTOS - VERSION MINIMAL
-- =====================================================

USE inventario;
GO

-- Eliminar objetos dependientes si existen
IF OBJECT_ID('v_productos_stock_bajo', 'V') IS NOT NULL
    DROP VIEW v_productos_stock_bajo;
GO

IF OBJECT_ID('TR_productos_update_timestamp', 'TR') IS NOT NULL
    DROP TRIGGER TR_productos_update_timestamp;
GO

IF OBJECT_ID('sp_buscar_productos_consolidado', 'P') IS NOT NULL
    DROP PROCEDURE sp_buscar_productos_consolidado;
GO

-- Eliminar tabla si existe
IF OBJECT_ID('productos', 'U') IS NOT NULL
    DROP TABLE productos;
GO

-- Crear tabla productos consolidada
CREATE TABLE productos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo NVARCHAR(50) UNIQUE NOT NULL,
    descripcion NVARCHAR(255) NOT NULL,
    
    -- Categorización
    categoria NVARCHAR(50) NOT NULL,
    subcategoria NVARCHAR(50) NULL,
    tipo NVARCHAR(100) NULL,
    
    -- Stock Management
    stock_actual DECIMAL(18,2) DEFAULT 0,
    stock_minimo DECIMAL(18,2) DEFAULT 0,
    stock_maximo DECIMAL(18,2) DEFAULT 1000,
    stock_reservado DECIMAL(18,2) DEFAULT 0,
    stock_disponible AS (stock_actual - stock_reservado),
    
    -- Pricing
    precio_unitario DECIMAL(18,2) DEFAULT 0,
    precio_promedio DECIMAL(18,2) DEFAULT 0,
    costo_unitario DECIMAL(18,2) DEFAULT 0,
    
    -- Physical Properties
    unidad_medida NVARCHAR(20) DEFAULT 'UND',
    ubicacion NVARCHAR(100) NULL,
    color NVARCHAR(50) NULL,
    material NVARCHAR(50) NULL,
    marca NVARCHAR(50) NULL,
    modelo NVARCHAR(50) NULL,
    acabado NVARCHAR(50) NULL,
    
    -- Supplier Info
    proveedor NVARCHAR(100) NULL,
    codigo_proveedor NVARCHAR(50) NULL,
    tiempo_entrega_dias INT DEFAULT 0,
    
    -- Additional Properties
    propiedades_especiales NVARCHAR(MAX) NULL,
    observaciones NVARCHAR(MAX) NULL,
    
    -- QR & Images
    codigo_qr NVARCHAR(255) NULL,
    imagen_url NVARCHAR(255) NULL,
    
    -- Control Fields
    estado NVARCHAR(20) DEFAULT 'ACTIVO',
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    usuario_creacion NVARCHAR(50) NULL,
    usuario_modificacion NVARCHAR(50) NULL
);

PRINT 'Tabla productos creada exitosamente';
GO

-- Crear índices básicos
CREATE INDEX IX_productos_categoria ON productos(categoria);
CREATE INDEX IX_productos_codigo ON productos(codigo);
CREATE INDEX IX_productos_descripcion ON productos(descripcion);

PRINT 'Índices creados exitosamente';
GO

-- Insertar datos de prueba para validar
INSERT INTO productos (codigo, descripcion, categoria, subcategoria, stock_actual, precio_unitario, proveedor)
VALUES 
    ('PERF-001', 'Perfil de Aluminio 20x20', 'PERFIL', 'ESTRUCTURAL', 100, 25.50, 'ALUMINIO SAC'),
    ('HERR-001', 'Bisagra Piano 1.5m', 'HERRAJE', 'BISAGRA', 50, 45.00, 'HERRAJES DEL NORTE'),
    ('VIDR-001', 'Vidrio Transparente 6mm', 'VIDRIO', 'TRANSPARENTE', 20, 85.00, 'CRISTALES SA'),
    ('MATT-001', 'Sellador Estructural', 'MATERIAL', 'SELLADOR', 30, 15.75, 'MATERIALES LIMA');

PRINT 'Datos de prueba insertados: 4 productos';
GO

-- Validar inserción
SELECT 
    categoria, 
    COUNT(*) as cantidad,
    AVG(precio_unitario) as precio_promedio
FROM productos 
GROUP BY categoria;

PRINT '=== TABLA PRODUCTOS CREADA Y VALIDADA ===';
GO