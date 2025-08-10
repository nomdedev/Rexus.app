-- =================================================================
-- SCRIPT DE MIGRACIÓN A ESTRUCTURA OPTIMIZADA (ADAPTADO)
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
        id_obra INT NOT NULL,           -- cambio de obra_id a id_obra para consistencia
        id_material INT NOT NULL,       -- cambio de material_id a id_material
        tipo_item VARCHAR(50) NOT NULL, -- 'material', 'herraje', 'accesorio'
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
        usuario VARCHAR(100),           -- cambio de usuario_pedido a usuario

        CONSTRAINT FK_pedidos_obra_obra FOREIGN KEY (id_obra) REFERENCES obras(id),
        CONSTRAINT FK_pedidos_obra_material FOREIGN KEY (id_material) REFERENCES inventario_perfiles(id)
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
        id_obra INT NOT NULL,         -- cambio de obra_id a id_obra para consistencia
        concepto VARCHAR(200) NOT NULL,
        tipo_pago VARCHAR(50),        -- 'adelanto', 'parcial', 'final', 'extra'
        monto DECIMAL(15,2) NOT NULL,
        fecha_pago DATE NOT NULL,
        fecha_vencimiento DATE,
        estado VARCHAR(50) DEFAULT 'pendiente',  -- pendiente, pagado, vencido, cancelado
        metodo_pago VARCHAR(50),      -- efectivo, transferencia, cheque, etc.
        comprobante VARCHAR(500),     -- Ruta al archivo del comprobante
        observaciones TEXT,
        usuario VARCHAR(200),         -- cambio de usuario_registro a usuario
        fecha_registro DATETIME DEFAULT GETDATE(),

        CONSTRAINT FK_pagos_obra_obra FOREIGN KEY (id_obra) REFERENCES obras(id)
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
IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_compra' AND xtype='U') AND EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_obra' AND xtype='U')
BEGIN
    INSERT INTO pedidos_obra (id_obra, id_material, tipo_item, cantidad_pedida, estado, fecha_pedido, usuario, observaciones)
    SELECT
        id_obra,
        1 as id_material, -- Asignar una clave temporal válida
        'material' as tipo_item,
        1 as cantidad_pedida, -- Cantidad por defecto
        ISNULL(estado, 'pendiente'),
        ISNULL(fecha, GETDATE()),
        ISNULL(usuario, 'sistema'),
        'Migrado desde pedidos_compra'
    FROM pedidos_compra
    WHERE id_obra IS NOT NULL;

    PRINT 'Datos migrados desde pedidos_compra';
END;

-- =================================================================
-- PASO 3: CREAR VISTAS PARA INTEGRACIÓN
-- =================================================================

-- 3.1 Vista para estado de materiales por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_materiales_obra' AND xtype='V')
    DROP VIEW v_estado_materiales_obra;
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_obra' AND xtype='U')
BEGIN
EXEC('
CREATE VIEW v_estado_materiales_obra AS
SELECT
    id_obra,
    CASE
        WHEN COUNT(*) = 0 THEN ''sin_pedidos''
        WHEN SUM(CASE WHEN estado = ''entregado'' THEN 1 ELSE 0 END) = COUNT(*) THEN ''completado''
        WHEN SUM(CASE WHEN estado IN (''pedido'', ''recibido'') THEN 1 ELSE 0 END) > 0 THEN ''en_proceso''
        ELSE ''pendiente''
    END as estado_material,
    COUNT(*) as total_pedidos,
    SUM(CASE WHEN estado = ''entregado'' THEN 1 ELSE 0 END) as pedidos_entregados,
    SUM(precio_total) as total_material
FROM pedidos_obra
WHERE tipo_item IN (''material'', ''herraje'')
GROUP BY id_obra;
')
PRINT 'Vista v_estado_materiales_obra creada';
END
GO

-- 3.2 Vista para estado de vidrios por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_vidrios_obra' AND xtype='V')
    DROP VIEW v_estado_vidrios_obra;
GO

CREATE VIEW v_estado_vidrios_obra AS
SELECT
    id_obra,
    CASE
        WHEN COUNT(*) = 0 THEN 'sin_pedidos'
        WHEN SUM(CASE WHEN estado IN ('entregado', 'instalado') THEN 1 ELSE 0 END) = COUNT(*) THEN 'completado'
        WHEN SUM(CASE WHEN estado IN ('en_produccion', 'listo') THEN 1 ELSE 0 END) > 0 THEN 'en_proceso'
        ELSE 'pendiente'
    END as estado_vidrios,
    COUNT(*) as total_vidrios,
    SUM(CASE WHEN estado IN ('entregado', 'instalado') THEN 1 ELSE 0 END) as vidrios_completados,
    COUNT(*) * 1000 as total_vidrios_aprox -- Sin precio_total usamos aproximación
FROM vidrios_por_obra
GROUP BY id_obra;
GO

-- 3.3 Vista para estado de pagos por obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='v_estado_pagos_obra' AND xtype='V')
    DROP VIEW v_estado_pagos_obra;
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obra' AND xtype='U')
BEGIN
EXEC('
CREATE VIEW v_estado_pagos_obra AS
SELECT
    id_obra,
    CASE
        WHEN COUNT(*) = 0 THEN ''sin_pagos''
        WHEN SUM(CASE WHEN estado = ''pagado'' THEN monto ELSE 0 END) >= SUM(monto) * 0.95 THEN ''completado''
        WHEN SUM(CASE WHEN estado = ''pagado'' THEN monto ELSE 0 END) > 0 THEN ''parcial''
        ELSE ''pendiente''
    END as estado_pago,
    COUNT(*) as total_pagos,
    SUM(monto) as monto_total,
    SUM(CASE WHEN estado = ''pagado'' THEN monto ELSE 0 END) as monto_pagado,
    (SUM(CASE WHEN estado = ''pagado'' THEN monto ELSE 0 END) / NULLIF(SUM(monto),0)) * 100 as porcentaje_pagado
FROM pagos_obra
GROUP BY id_obra;
')
PRINT 'Vista v_estado_pagos_obra creada';
END
GO

-- =================================================================
-- PASO 4: CREAR FUNCIONES PARA LOS MODELOS
-- =================================================================

-- 4.1 Función para obtener estado de materiales
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_material_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_material_obra;
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_obra' AND xtype='U')
BEGIN
EXEC('
CREATE FUNCTION fn_obtener_estado_material_obra(@id_obra INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_material
    FROM v_estado_materiales_obra
    WHERE id_obra = @id_obra;

    RETURN ISNULL(@estado, ''sin_pedidos'');
END;
')
PRINT 'Función fn_obtener_estado_material_obra creada';
END
GO

-- 4.2 Función para obtener estado de vidrios
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_vidrios_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_vidrios_obra;
GO

CREATE FUNCTION fn_obtener_estado_vidrios_obra(@id_obra INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_vidrios
    FROM v_estado_vidrios_obra
    WHERE id_obra = @id_obra;

    RETURN ISNULL(@estado, 'sin_pedidos');
END;
GO

-- 4.3 Función para obtener estado de pagos
IF EXISTS (SELECT * FROM sysobjects WHERE name='fn_obtener_estado_pagos_obra' AND xtype='FN')
    DROP FUNCTION fn_obtener_estado_pagos_obra;
GO

IF EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obra' AND xtype='U')
BEGIN
EXEC('
CREATE FUNCTION fn_obtener_estado_pagos_obra(@id_obra INT)
RETURNS VARCHAR(50)
AS
BEGIN
    DECLARE @estado VARCHAR(50);

    SELECT @estado = estado_pago
    FROM v_estado_pagos_obra
    WHERE id_obra = @id_obra;

    RETURN ISNULL(@estado, ''sin_pagos'');
END;
')
PRINT 'Función fn_obtener_estado_pagos_obra creada';
END
GO

-- =================================================================
-- PASO 5: VERIFICACIÓN FINAL
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
SELECT 'DATOS - TABLAS CLAVE' as Categoria;
SELECT 'obras' as Tabla, COUNT(*) as Registros FROM obras;
SELECT 'inventario_perfiles' as Tabla, COUNT(*) as Registros FROM inventario_perfiles;
SELECT 'vidrios_por_obra' as Tabla, COUNT(*) as Registros FROM vidrios_por_obra;

-- Contar registros en nuevas tablas
IF EXISTS (SELECT * FROM sysobjects WHERE name='pedidos_obra' AND xtype='U')
    SELECT 'pedidos_obra' as Tabla, COUNT(*) as Registros FROM pedidos_obra;
ELSE
    SELECT 'pedidos_obra' as Tabla, 'NO EXISTE' as Registros;

IF EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obra' AND xtype='U')
    SELECT 'pagos_obra' as Tabla, COUNT(*) as Registros FROM pagos_obra;
ELSE
    SELECT 'pagos_obra' as Tabla, 'NO EXISTE' as Registros;

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
PRINT 'MIGRACIÓN COMPLETADA';
PRINT 'Próximo paso: Actualizar los modelos de Python para usar las nuevas tablas';
PRINT '=================================================================';
