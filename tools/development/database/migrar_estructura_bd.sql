-- =================================================================
-- SCRIPT DE MIGRACIÓN A ESTRUCTURA OPTIMIZADA
-- Base de datos: inventario
-- Fecha: 25 de junio de 2025
-- Objetivo: Simplificar estructura y optimizar integración cruzada
-- =================================================================

USE inventario;
GO

-- =================================================================
-- PASO 1: CREAR TABLAS NUEVAS (SI NO EXISTEN)
-- =================================================================

-- 1.1 Verificar y crear tabla de pedidos unificada
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_obra' AND xtype='U')
BEGIN
    CREATE TABLE pedidos_obra (
        id INT PRIMARY KEY IDENTITY(1,1),
        obra_id INT NOT NULL,
        material_id INT NOT NULL,
        tipo_item VARCHAR(50) NOT NULL,     -- 'material', 'herraje', 'accesorio'
        cantidad_pedida DECIMAL(10,3) NOT NULL,
        cantidad_entregada DECIMAL(10,3) DEFAULT 0,
        estado VARCHAR(50) DEFAULT 'pendiente',  -- pendiente, pedido, recibido, entregado, cancelado
        precio_unitario DECIMAL(10,2),
        precio_total DECIMAL(15,2),
        fecha_pedido DATETIME DEFAULT GETDATE(),
        fecha_entrega_estimada DATE,
        fecha_entrega_real DATE,
        proveedor VARCHAR(200),
        observaciones TEXT,
        usuario_pedido INT,
        usuario_entrega INT,

        CONSTRAINT FK_pedidos_obra_obra FOREIGN KEY (obra_id) REFERENCES obras(id),
        CONSTRAINT FK_pedidos_obra_material FOREIGN KEY (material_id) REFERENCES inventario_perfiles(id)
    );

    PRINT 'Tabla pedidos_obra creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla pedidos_obra ya existe';
END;

-- 1.2 Verificar y crear tabla de pagos unificada
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obra' AND xtype='U')
BEGIN
    CREATE TABLE pagos_obra (
        id INT PRIMARY KEY IDENTITY(1,1),
        obra_id INT NOT NULL,
        concepto VARCHAR(200) NOT NULL,
        tipo_pago VARCHAR(50),               -- 'adelanto', 'parcial', 'final', 'extra'
        monto DECIMAL(15,2) NOT NULL,
        fecha_pago DATE NOT NULL,
        fecha_vencimiento DATE,
        estado VARCHAR(50) DEFAULT 'pendiente',  -- pendiente, pagado, vencido, cancelado
        metodo_pago VARCHAR(50),             -- efectivo, transferencia, cheque, etc.
        comprobante VARCHAR(500),            -- Ruta al archivo del comprobante
        observaciones TEXT,
        usuario_registro INT,
        fecha_registro DATETIME DEFAULT GETDATE(),

        CONSTRAINT FK_pagos_obra_obra FOREIGN KEY (obra_id) REFERENCES obras(id)
    );

    PRINT 'Tabla pagos_obra creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla pagos_obra ya existe';
END;

-- =================================================================
-- PASO 2: MIGRAR DATOS EXISTENTES
-- =================================================================

-- 2.1 Migrar datos de pedidos_compra a pedidos_obra (si existe)
IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_compra' AND xtype='U')
BEGIN
    INSERT INTO pedidos_obra (obra_id, material_id, tipo_item, cantidad_pedida, estado, fecha_pedido, usuario_pedido, observaciones)
    SELECT
        obra_id,
        material_id,
        'material' as tipo_item,
        cantidad,
        ISNULL(estado, 'pendiente'),
        ISNULL(fecha, GETDATE()),
        ISNULL(usuario, 1),
        'Migrado desde pedidos_compra'
    FROM pedidos_compra
    WHERE obra_id IS NOT NULL AND material_id IS NOT NULL;

    PRINT 'Datos migrados desde pedidos_compra';
END;

-- 2.2 Migrar datos de otros pedidos si existen
IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_material' AND xtype='U')
BEGIN
    INSERT INTO pedidos_obra (obra_id, material_id, tipo_item, cantidad_pedida, estado, fecha_pedido)
    SELECT
        obra_id,
        material_id,
        'material' as tipo_item,
        cantidad,
        ISNULL(estado, 'pendiente'),
        ISNULL(fecha_pedido, GETDATE())
    FROM pedidos_material
    WHERE obra_id IS NOT NULL AND material_id IS NOT NULL;

    PRINT 'Datos migrados desde pedidos_material';
END;

-- 2.3 Migrar datos de herrajes si existen
IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_herrajes' AND xtype='U')
BEGIN
    INSERT INTO pedidos_obra (obra_id, material_id, tipo_item, cantidad_pedida, estado, fecha_pedido)
    SELECT
        obra_id,
        herraje_id as material_id,
        'herraje' as tipo_item,
        cantidad,
        ISNULL(estado, 'pendiente'),
        ISNULL(fecha_pedido, GETDATE())
    FROM pedidos_herrajes
    WHERE obra_id IS NOT NULL AND herraje_id IS NOT NULL;

    PRINT 'Datos migrados desde pedidos_herrajes';
END;

-- 2.4 Migrar datos de pagos si existen
IF EXISTS (SELECT * FROM sysobjects WHERE name='pagos_pedidos' AND xtype='U')
BEGIN
    INSERT INTO pagos_obra (obra_id, concepto, monto, fecha_pago, estado, usuario_registro)
    SELECT
        obra_id,
        ISNULL(modulo + ' - ' + tipo_pedido, 'Concepto migrado') as concepto,
        monto,
        ISNULL(fecha_pago, fecha) as fecha_pago,
        ISNULL(estado, 'pendiente'),
        ISNULL(usuario, 1)
    FROM pagos_pedidos
    WHERE obra_id IS NOT NULL AND monto IS NOT NULL;

    PRINT 'Datos migrados desde pagos_pedidos';
END;

-- =================================================================
-- PASO 3: INSERTAR DATOS DE EJEMPLO PARA TESTING
-- =================================================================

-- 3.1 Verificar si hay obras para testing
DECLARE @obra_count INT;
SELECT @obra_count = COUNT(*) FROM obras;

IF @obra_count = 0
BEGIN
    -- Insertar obras de ejemplo
    INSERT INTO obras (nombre, cliente, estado, fecha_inicio, fecha_entrega_estimada, presupuesto_total, usuario_responsable)
    VALUES
    ('Casa Familia Pérez', 'Juan Pérez', 'activo', '2025-01-15', '2025-03-15', 250000.00, 1),
    ('Oficina Comercial', 'Empresa ABC SA', 'activo', '2025-02-01', '2025-04-30', 480000.00, 1),
    ('Departamento Centro', 'María González', 'completado', '2024-12-01', '2025-02-15', 180000.00, 1);

    PRINT 'Obras de ejemplo insertadas';
END;

-- 3.2 Verificar si hay materiales para testing
DECLARE @material_count INT;
SELECT @material_count = COUNT(*) FROM inventario_perfiles;

IF @material_count = 0
BEGIN
    -- Insertar materiales de ejemplo
    INSERT INTO inventario_perfiles (codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, precio_unitario)
    VALUES
    ('PERF-ALU-001', 'Perfil Aluminio 40x20mm', 'Perfil', 'm', 150.5, 10.0, 2500.00),
    ('TORN-INX-001', 'Tornillo Inoxidable 6x30', 'Tornillo', 'unidad', 500, 50, 15.50),
    ('CHAP-GAL-001', 'Chapa Galvanizada 0.8mm', 'Chapa', 'm2', 25.0, 5.0, 8500.00);

    PRINT 'Materiales de ejemplo insertados';
END;

-- 3.3 Insertar pedidos de ejemplo
DECLARE @obra1_id INT, @obra2_id INT;
SELECT TOP 1 @obra1_id = id FROM obras ORDER BY id;
SELECT @obra2_id = id FROM obras WHERE id > @obra1_id ORDER BY id;

DECLARE @material1_id INT, @material2_id INT, @material3_id INT;
SELECT TOP 1 @material1_id = id FROM inventario_perfiles ORDER BY id;
SELECT @material2_id = id FROM inventario_perfiles WHERE id > @material1_id ORDER BY id;
SELECT @material3_id = id FROM inventario_perfiles WHERE id > @material2_id ORDER BY id;

IF @obra1_id IS NOT NULL AND @material1_id IS NOT NULL
BEGIN
    -- Solo insertar si no hay pedidos ya
    IF NOT EXISTS (SELECT * FROM pedidos_obra)
    BEGIN
        INSERT INTO pedidos_obra (obra_id, material_id, tipo_item, cantidad_pedida, estado, precio_unitario, precio_total, usuario_pedido)
        VALUES
        (@obra1_id, @material1_id, 'material', 25.0, 'pendiente', 2500.00, 62500.00, 1),
        (@obra1_id, @material2_id, 'herraje', 100, 'pedido', 15.50, 1550.00, 1);

        IF @obra2_id IS NOT NULL AND @material3_id IS NOT NULL
        BEGIN
            INSERT INTO pedidos_obra (obra_id, material_id, tipo_item, cantidad_pedida, cantidad_entregada, estado, precio_unitario, precio_total, usuario_pedido)
            VALUES
            (@obra2_id, @material3_id, 'material', 45.0, 45.0, 'entregado', 8500.00, 382500.00, 1);
        END;

        PRINT 'Pedidos de ejemplo insertados';
    END;
END;

-- 3.4 Insertar vidrios de ejemplo si no existen
IF NOT EXISTS (SELECT * FROM vidrios_por_obra)
BEGIN
    IF @obra1_id IS NOT NULL
    BEGIN
        INSERT INTO vidrios_por_obra (obra_id, tipo_vidrio, ancho, alto, espesor, color, cantidad, estado, precio_unitario, precio_total, usuario_pedido)
        VALUES
        (@obra1_id, 'Templado', 1200.00, 800.00, 6.00, 'Incoloro', 2, 'en_produccion', 25000.00, 50000.00, 1),
        (@obra1_id, 'Laminado', 1500.00, 2000.00, 8.00, 'Verde', 1, 'pendiente', 45000.00, 45000.00, 1);

        IF @obra2_id IS NOT NULL
        BEGIN
            INSERT INTO vidrios_por_obra (obra_id, tipo_vidrio, ancho, alto, espesor, color, cantidad, estado, precio_unitario, precio_total, usuario_pedido)
            VALUES
            (@obra2_id, 'DVH', 1000.00, 1200.00, 20.00, 'Incoloro', 8, 'listo', 38000.00, 304000.00, 1);
        END;

        PRINT 'Vidrios de ejemplo insertados';
    END;
END;

-- 3.5 Insertar pagos de ejemplo
IF NOT EXISTS (SELECT * FROM pagos_obra)
BEGIN
    IF @obra1_id IS NOT NULL
    BEGIN
        INSERT INTO pagos_obra (obra_id, concepto, tipo_pago, monto, fecha_pago, estado, metodo_pago, usuario_registro)
        VALUES
        (@obra1_id, 'Material - Perfiles', 'adelanto', 30000.00, '2025-01-10', 'pagado', 'transferencia', 1),
        (@obra1_id, 'Vidrios - Templados', 'parcial', 25000.00, '2025-01-15', 'pendiente', 'cheque', 1);

        IF @obra2_id IS NOT NULL
        BEGIN
            INSERT INTO pagos_obra (obra_id, concepto, tipo_pago, monto, fecha_pago, estado, metodo_pago, usuario_registro)
            VALUES
            (@obra2_id, 'Material - Chapas', 'final', 382500.00, '2025-01-25', 'pagado', 'efectivo', 1);
        END;

        PRINT 'Pagos de ejemplo insertados';
    END;
END;

-- =================================================================
-- PASO 4: CREAR VISTAS PARA INTEGRACIÓN
-- =================================================================

-- 4.1 Vista para estado de materiales por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_materiales_obra' AND xtype='V')
    DROP VIEW v_estado_materiales_obra;
GO

CREATE VIEW v_estado_materiales_obra AS
SELECT
    obra_id,
    CASE
        WHEN COUNT(*) = 0 THEN 'sin_pedidos'
        WHEN SUM(CASE WHEN estado = 'entregado' THEN 1 ELSE 0 END) = COUNT(*) THEN 'completado'
        WHEN SUM(CASE WHEN estado IN ('pedido', 'recibido') THEN 1 ELSE 0 END) > 0 THEN 'en_proceso'
        ELSE 'pendiente'
    END as estado_material,
    COUNT(*) as total_pedidos,
    SUM(CASE WHEN estado = 'entregado' THEN 1 ELSE 0 END) as pedidos_entregados,
    SUM(precio_total) as total_material
FROM pedidos_obra
WHERE tipo_item IN ('material', 'herraje')
GROUP BY obra_id;
GO

-- 4.2 Vista para estado de vidrios por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_vidrios_obra' AND xtype='V')
    DROP VIEW v_estado_vidrios_obra;
GO

CREATE VIEW v_estado_vidrios_obra AS
SELECT
    obra_id,
    CASE
        WHEN COUNT(*) = 0 THEN 'sin_pedidos'
        WHEN SUM(CASE WHEN estado IN ('entregado', 'instalado') THEN 1 ELSE 0 END) = COUNT(*) THEN 'completado'
        WHEN SUM(CASE WHEN estado IN ('en_produccion', 'listo') THEN 1 ELSE 0 END) > 0 THEN 'en_proceso'
        ELSE 'pendiente'
    END as estado_vidrios,
    COUNT(*) as total_vidrios,
    SUM(CASE WHEN estado IN ('entregado', 'instalado') THEN 1 ELSE 0 END) as vidrios_completados,
    SUM(precio_total) as total_vidrios
FROM vidrios_por_obra
GROUP BY obra_id;
GO

-- 4.3 Vista para estado de pagos por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_pagos_obra' AND xtype='V')
    DROP VIEW v_estado_pagos_obra;
GO

CREATE VIEW v_estado_pagos_obra AS
SELECT
    obra_id,
    CASE
        WHEN COUNT(*) = 0 THEN 'sin_pagos'
        WHEN SUM(CASE WHEN estado = 'pagado' THEN monto ELSE 0 END) >= SUM(monto) * 0.95 THEN 'completado'
        WHEN SUM(CASE WHEN estado = 'pagado' THEN monto ELSE 0 END) > 0 THEN 'parcial'
        ELSE 'pendiente'
    END as estado_pago,
    COUNT(*) as total_pagos,
    SUM(monto) as monto_total,
    SUM(CASE WHEN estado = 'pagado' THEN monto ELSE 0 END) as monto_pagado,
    (SUM(CASE WHEN estado = 'pagado' THEN monto ELSE 0 END) / SUM(monto)) * 100 as porcentaje_pagado
FROM pagos_obra
GROUP BY obra_id;
GO

-- =================================================================
-- PASO 5: CREAR FUNCIONES PARA LOS MODELOS
-- =================================================================

-- 5.1 Función para obtener estado de materiales
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_material_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_material_obra;
GO

CREATE FUNCTION fn_obtener_estado_material_obra(@obra_id INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_material
    FROM v_estado_materiales_obra
    WHERE obra_id = @obra_id;

    RETURN ISNULL(@estado, 'sin_pedidos');
END;
GO

-- 5.2 Función para obtener estado de vidrios
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_vidrios_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_vidrios_obra;
GO

CREATE FUNCTION fn_obtener_estado_vidrios_obra(@obra_id INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_vidrios
    FROM v_estado_vidrios_obra
    WHERE obra_id = @obra_id;

    RETURN ISNULL(@estado, 'sin_pedidos');
END;
GO

-- 5.3 Función para obtener estado de pagos
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_pagos_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_pagos_obra;
GO

CREATE FUNCTION fn_obtener_estado_pagos_obra(@obra_id INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_pago
    FROM v_estado_pagos_obra
    WHERE obra_id = @obra_id;

    RETURN ISNULL(@estado, 'sin_pagos');
END;
GO

-- =================================================================
-- PASO 6: VERIFICACIÓN FINAL
-- =================================================================

PRINT '';
PRINT '=================================================================';
PRINT 'MIGRACIÓN COMPLETADA - RESUMEN';
PRINT '=================================================================';

-- Verificar tablas creadas
SELECT 'TABLAS PRINCIPALES' as Categoria, name as Tabla, 'Existe' as Estado
FROM sysobjects
WHERE name IN ('obras', 'inventario_perfiles', 'pedidos_obra', 'vidrios_por_obra', 'pagos_obra')
AND xtype = 'U'
ORDER BY name;

-- Contar registros
SELECT 'DATOS' as Categoria,
       (SELECT COUNT(*) FROM obras) as Obras,
       (SELECT COUNT(*) FROM inventario_perfiles) as Materiales,
       (SELECT COUNT(*) FROM pedidos_obra) as Pedidos,
       (SELECT COUNT(*) FROM vidrios_por_obra) as Vidrios,
       (SELECT COUNT(*) FROM pagos_obra) as Pagos;

-- Verificar vistas
SELECT 'VISTAS' as Categoria, name as Vista, 'Creada' as Estado
FROM sysobjects
WHERE name LIKE 'v_estado_%'
AND xtype = 'V'
ORDER BY name;

-- Verificar funciones
SELECT 'FUNCIONES' as Categoria, name as Funcion, 'Creada' as Estado
FROM sysobjects
WHERE name LIKE 'fn_obtener_%'
AND xtype = 'FN'
ORDER BY name;

PRINT '';
PRINT 'MIGRACIÓN COMPLETADA EXITOSAMENTE';
PRINT 'Próximo paso: Actualizar los modelos de Python para usar las nuevas tablas';
PRINT '=================================================================';
