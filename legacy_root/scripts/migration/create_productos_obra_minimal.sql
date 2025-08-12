-- =====================================================
-- CREAR TABLA PRODUCTOS_OBRA - VERSION MINIMAL
-- =====================================================

USE inventario;
GO

-- Eliminar tabla si existe
IF OBJECT_ID('productos_obra', 'U') IS NOT NULL
    DROP TABLE productos_obra;
GO

-- Crear tabla productos_obra consolidada
CREATE TABLE productos_obra (
    id INT IDENTITY(1,1) PRIMARY KEY,
    obra_id INT NOT NULL,
    producto_id INT NOT NULL,
    
    -- Cantidades
    cantidad_requerida DECIMAL(18,2) NOT NULL DEFAULT 0,
    cantidad_asignada DECIMAL(18,2) DEFAULT 0,
    cantidad_utilizada DECIMAL(18,2) DEFAULT 0,
    cantidad_desperdicio DECIMAL(18,2) DEFAULT 0,
    
    -- Etapa de la obra
    etapa_obra NVARCHAR(50) DEFAULT 'GENERAL',
    
    -- Precios al momento de asignación
    precio_unitario_asignacion DECIMAL(18,2) DEFAULT 0,
    costo_total_estimado AS (cantidad_requerida * precio_unitario_asignacion),
    
    -- Estado y prioridad
    estado NVARCHAR(20) DEFAULT 'PENDIENTE',
    prioridad NVARCHAR(20) DEFAULT 'MEDIA',
    
    -- Notas
    observaciones NVARCHAR(MAX) NULL,
    notas_instalacion NVARCHAR(MAX) NULL,
    
    -- Control de fechas
    fecha_asignacion DATETIME DEFAULT GETDATE(),
    fecha_requerida DATETIME NULL,
    fecha_utilizado DATETIME NULL,
    
    -- Auditoría
    usuario_asignacion NVARCHAR(50) DEFAULT 'SISTEMA',
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    activo BIT DEFAULT 1,
    
    -- Foreign keys (no se crean constraints por simplicidad)
    -- FOREIGN KEY (obra_id) REFERENCES detalles_obra(id),
    -- FOREIGN KEY (producto_id) REFERENCES productos(id)
);

PRINT 'Tabla productos_obra creada exitosamente';
GO

-- Crear índices básicos
CREATE INDEX IX_productos_obra_obra_id ON productos_obra(obra_id);
CREATE INDEX IX_productos_obra_producto_id ON productos_obra(producto_id);
CREATE INDEX IX_productos_obra_etapa ON productos_obra(etapa_obra);
CREATE INDEX IX_productos_obra_estado ON productos_obra(estado);

PRINT 'Índices creados exitosamente';
GO

-- Insertar datos de prueba
INSERT INTO productos_obra (obra_id, producto_id, cantidad_requerida, etapa_obra, precio_unitario_asignacion, observaciones)
VALUES 
    (1, 1, 50.00, 'ESTRUCTURA', 25.50, 'Perfiles para estructura principal'),
    (1, 2, 10.00, 'ACABADOS', 45.00, 'Bisagras para puertas'),
    (2, 3, 8.50, 'VIDRIADO', 85.00, 'Vidrios para ventanas'),
    (2, 4, 5.00, 'SELLADO', 15.75, 'Sellador para acabados');

PRINT 'Datos de prueba insertados: 4 asignaciones';
GO

-- Validar inserción
SELECT 
    po.id,
    po.obra_id,
    p.codigo,
    p.descripcion,
    po.cantidad_requerida,
    po.etapa_obra,
    po.costo_total_estimado
FROM productos_obra po
INNER JOIN productos p ON po.producto_id = p.id
ORDER BY po.obra_id, po.etapa_obra;

PRINT '=== TABLA PRODUCTOS_OBRA CREADA Y VALIDADA ===';
GO