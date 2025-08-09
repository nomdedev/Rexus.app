-- =====================================================================
-- MIGRACIÓN DE DATOS A TABLA PRODUCTOS CONSOLIDADA - REXUS.APP
-- =====================================================================
-- Propósito: Migrar datos de tablas existentes (inventario, herrajes)
--           a la nueva tabla productos consolidada
-- NOTA: Vidrios se mantienen en tabla separada por características únicas
-- ADVERTENCIA: Crear backup antes de ejecutar este script
-- Fecha: 2025-08-09
-- Versión: 1.1 (Ajustado sin vidrios)
-- =====================================================================

-- Verificar que la tabla productos existe
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='productos' AND xtype='U')
BEGIN
    PRINT 'ERROR: La tabla productos no existe. Ejecute consolidar_productos.sql primero.';
    RETURN;
END

PRINT '========================================';
PRINT 'INICIANDO MIGRACIÓN DE DATOS';
PRINT '========================================';

-- =====================================================================
-- 1. MIGRAR DATOS DE TABLA INVENTARIO
-- =====================================================================

PRINT 'Migrando datos de inventario...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='inventario' AND xtype='U')
BEGIN
    DECLARE @inventario_migrados INT = 0;
    
    INSERT INTO productos (
        codigo, nombre, descripcion, tipo_producto, categoria, subcategoria,
        precio_compra, precio_venta, stock, stock_minimo, unidad_medida,
        proveedor_codigo, estado, usuario_creacion, fecha_creacion, 
        fecha_modificacion, activo
    )
    SELECT 
        ISNULL(codigo, 'INV-' + CAST(ROW_NUMBER() OVER (ORDER BY id) AS varchar)) as codigo,
        ISNULL(nombre, 'Producto Sin Nombre') as nombre,
        ISNULL(descripcion, '') as descripcion,
        'INVENTARIO' as tipo_producto,
        ISNULL(categoria, 'GENERAL') as categoria,
        ISNULL(subcategoria, NULL) as subcategoria,
        ISNULL(precio_compra, 0.00) as precio_compra,
        ISNULL(precio, 0.00) as precio_venta,
        ISNULL(stock, 0) as stock,
        ISNULL(stock_minimo, 0) as stock_minimo,
        ISNULL(unidad, 'UNIDAD') as unidad_medida,
        ISNULL(codigo_proveedor, NULL) as proveedor_codigo,
        CASE 
            WHEN ISNULL(activo, 1) = 1 THEN 'ACTIVO'
            ELSE 'INACTIVO'
        END as estado,
        ISNULL(usuario_creacion, 'MIGRATION') as usuario_creacion,
        ISNULL(fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(fecha_modificacion, GETDATE()) as fecha_modificacion,
        ISNULL(activo, 1) as activo
    FROM inventario
    WHERE NOT EXISTS (
        SELECT 1 FROM productos p 
        WHERE p.codigo = ISNULL(inventario.codigo, 'INV-' + CAST(inventario.id AS varchar))
          AND p.tipo_producto = 'INVENTARIO'
    );
    
    SET @inventario_migrados = @@ROWCOUNT;
    PRINT 'Inventario migrado: ' + CAST(@inventario_migrados AS varchar) + ' registros';
END
ELSE
BEGIN
    PRINT 'Tabla inventario no existe - saltando migración';
END

-- =====================================================================
-- 2. MIGRAR DATOS DE TABLA HERRAJES
-- =====================================================================

PRINT 'Migrando datos de herrajes...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes' AND xtype='U')
BEGIN
    DECLARE @herrajes_migrados INT = 0;
    
    INSERT INTO productos (
        codigo, nombre, descripcion, tipo_producto, categoria,
        precio_compra, precio_venta, stock, stock_minimo, unidad_medida,
        tipo_herraje, acabado, material, estado, usuario_creacion, 
        fecha_creacion, fecha_modificacion, activo
    )
    SELECT 
        ISNULL(codigo, 'HER-' + CAST(ROW_NUMBER() OVER (ORDER BY id) AS varchar)) as codigo,
        ISNULL(nombre, 'Herraje Sin Nombre') as nombre,
        ISNULL(descripcion, '') as descripcion,
        'HERRAJE' as tipo_producto,
        ISNULL(categoria, 'HERRAJES') as categoria,
        ISNULL(precio_compra, 0.00) as precio_compra,
        ISNULL(precio, 0.00) as precio_venta,
        ISNULL(stock, 0) as stock,
        ISNULL(stock_minimo, 0) as stock_minimo,
        ISNULL(unidad, 'UNIDAD') as unidad_medida,
        ISNULL(tipo, NULL) as tipo_herraje,
        ISNULL(acabado, NULL) as acabado,
        ISNULL(material, NULL) as material,
        CASE 
            WHEN ISNULL(activo, 1) = 1 THEN 'ACTIVO'
            ELSE 'INACTIVO'
        END as estado,
        ISNULL(usuario_creacion, 'MIGRATION') as usuario_creacion,
        ISNULL(fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(fecha_modificacion, GETDATE()) as fecha_modificacion,
        ISNULL(activo, 1) as activo
    FROM herrajes
    WHERE NOT EXISTS (
        SELECT 1 FROM productos p 
        WHERE p.codigo = ISNULL(herrajes.codigo, 'HER-' + CAST(herrajes.id AS varchar))
          AND p.tipo_producto = 'HERRAJE'
    );
    
    SET @herrajes_migrados = @@ROWCOUNT;
    PRINT 'Herrajes migrados: ' + CAST(@herrajes_migrados AS varchar) + ' registros';
END
ELSE
BEGIN
    PRINT 'Tabla herrajes no existe - saltando migración';
END

-- =====================================================================
-- 3. NOTA SOBRE VIDRIOS
-- =====================================================================

PRINT 'NOTA: Los vidrios NO se migran a la tabla consolidada';
PRINT 'Los vidrios mantienen su tabla separada por sus características únicas:';
PRINT '- Medidas exactas y personalizadas';  
PRINT '- Espesores específicos por proyecto';
PRINT '- Cortes y conformaciones particulares';
PRINT 'La tabla vidrios se conserva intacta.';

-- =====================================================================
-- 4. MIGRAR RELACIONES PRODUCTO-OBRA
-- =====================================================================

PRINT 'Migrando relaciones producto-obra...';

-- Migrar herrajes_obra
IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes_obra' AND xtype='U')
BEGIN
    INSERT INTO productos_obras (
        producto_id, obra_id, cantidad_requerida, cantidad_asignada,
        precio_unitario, estado, usuario_creacion, fecha_creacion, activo
    )
    SELECT 
        p.id as producto_id,
        ho.obra_id,
        ISNULL(ho.cantidad, 0) as cantidad_requerida,
        ISNULL(ho.cantidad_asignada, 0) as cantidad_asignada,
        ISNULL(ho.precio, 0.00) as precio_unitario,
        CASE 
            WHEN ISNULL(ho.activo, 1) = 1 THEN 'ASIGNADO'
            ELSE 'CANCELADO'
        END as estado,
        'MIGRATION' as usuario_creacion,
        ISNULL(ho.fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(ho.activo, 1) as activo
    FROM herrajes_obra ho
    INNER JOIN herrajes h ON ho.herraje_id = h.id
    INNER JOIN productos p ON p.codigo = h.codigo AND p.tipo_producto = 'HERRAJE'
    WHERE NOT EXISTS (
        SELECT 1 FROM productos_obras po 
        WHERE po.producto_id = p.id AND po.obra_id = ho.obra_id
    );
    
    PRINT 'Relaciones herrajes-obra migradas: ' + CAST(@@ROWCOUNT AS varchar) + ' registros';
END

-- NOTA: Las relaciones vidrios_obra se mantienen en su tabla original
-- No se migran porque los vidrios conservan su tabla separada
PRINT 'NOTA: Las relaciones vidrios_obra se mantienen en tabla original';

-- =====================================================================
-- 5. MIGRAR MOVIMIENTOS DE INVENTARIO
-- =====================================================================

PRINT 'Migrando movimientos de inventario...';

IF EXISTS (SELECT * FROM sysobjects WHERE name='inventario_movimientos' AND xtype='U')
BEGIN
    INSERT INTO productos_movimientos (
        producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo,
        precio_unitario, costo_total, documento_referencia, motivo, 
        observaciones, usuario_creacion, fecha_creacion
    )
    SELECT 
        p.id as producto_id,
        ISNULL(im.tipo, 'AJUSTE') as tipo_movimiento,
        ISNULL(im.cantidad, 0) as cantidad,
        ISNULL(im.stock_anterior, 0) as stock_anterior,
        ISNULL(im.stock_nuevo, 0) as stock_nuevo,
        ISNULL(im.precio_unitario, 0.00) as precio_unitario,
        ISNULL(im.cantidad * im.precio_unitario, 0.00) as costo_total,
        ISNULL(im.documento, NULL) as documento_referencia,
        ISNULL(im.motivo, 'Migración de datos') as motivo,
        ISNULL(im.observaciones, '') as observaciones,
        ISNULL(im.usuario, 'MIGRATION') as usuario_creacion,
        ISNULL(im.fecha, GETDATE()) as fecha_creacion
    FROM inventario_movimientos im
    INNER JOIN inventario i ON im.producto_id = i.id
    INNER JOIN productos p ON p.codigo = i.codigo AND p.tipo_producto = 'INVENTARIO'
    WHERE NOT EXISTS (
        SELECT 1 FROM productos_movimientos pm 
        WHERE pm.producto_id = p.id 
          AND pm.fecha_creacion = im.fecha 
          AND pm.cantidad = im.cantidad
    );
    
    PRINT 'Movimientos migrados: ' + CAST(@@ROWCOUNT AS varchar) + ' registros';
END

-- =====================================================================
-- 6. VERIFICAR INTEGRIDAD DE LA MIGRACIÓN
-- =====================================================================

PRINT '';
PRINT 'VERIFICANDO INTEGRIDAD DE LA MIGRACIÓN...';
PRINT '==========================================';

-- Resumen por tipo de producto
SELECT 
    tipo_producto,
    COUNT(*) as cantidad,
    SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as activos,
    SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as en_estado_activo,
    SUM(stock) as stock_total,
    SUM(CASE WHEN stock <= stock_minimo THEN 1 ELSE 0 END) as con_stock_bajo
FROM productos
GROUP BY tipo_producto
ORDER BY tipo_producto;

-- Verificar duplicados por código
SELECT codigo, COUNT(*) as duplicados
FROM productos
GROUP BY codigo
HAVING COUNT(*) > 1;

-- Estadísticas generales
DECLARE @total_productos INT, @total_relaciones INT, @total_movimientos INT;

SELECT @total_productos = COUNT(*) FROM productos;
SELECT @total_relaciones = COUNT(*) FROM productos_obras;
SELECT @total_movimientos = COUNT(*) FROM productos_movimientos;

PRINT '';
PRINT 'ESTADÍSTICAS DE MIGRACIÓN:';
PRINT '- Total productos migrados: ' + CAST(@total_productos AS varchar);
PRINT '- Total relaciones obra: ' + CAST(@total_relaciones AS varchar);
PRINT '- Total movimientos: ' + CAST(@total_movimientos AS varchar);

-- =====================================================================
-- 7. CREAR RESPALDO DE VALIDACIÓN
-- =====================================================================

PRINT '';
PRINT 'Creando respaldo de validación...';

-- Tabla temporal con resumen de migración
IF EXISTS (SELECT * FROM sysobjects WHERE name='temp_migracion_summary' AND xtype='U')
    DROP TABLE temp_migracion_summary;

CREATE TABLE temp_migracion_summary (
    tabla_origen varchar(50),
    registros_origen int,
    registros_migrados int,
    porcentaje_migracion decimal(5,2),
    fecha_migracion datetime DEFAULT GETDATE()
);

-- Insertar estadísticas de inventario
IF EXISTS (SELECT * FROM sysobjects WHERE name='inventario' AND xtype='U')
BEGIN
    INSERT INTO temp_migracion_summary (tabla_origen, registros_origen, registros_migrados, porcentaje_migracion)
    SELECT 
        'inventario',
        (SELECT COUNT(*) FROM inventario),
        (SELECT COUNT(*) FROM productos WHERE tipo_producto = 'INVENTARIO'),
        CASE 
            WHEN (SELECT COUNT(*) FROM inventario) > 0 
            THEN ((SELECT COUNT(*) FROM productos WHERE tipo_producto = 'INVENTARIO') * 100.0 / (SELECT COUNT(*) FROM inventario))
            ELSE 0
        END;
END

-- Insertar estadísticas de herrajes
IF EXISTS (SELECT * FROM sysobjects WHERE name='herrajes' AND xtype='U')
BEGIN
    INSERT INTO temp_migracion_summary (tabla_origen, registros_origen, registros_migrados, porcentaje_migracion)
    SELECT 
        'herrajes',
        (SELECT COUNT(*) FROM herrajes),
        (SELECT COUNT(*) FROM productos WHERE tipo_producto = 'HERRAJE'),
        CASE 
            WHEN (SELECT COUNT(*) FROM herrajes) > 0 
            THEN ((SELECT COUNT(*) FROM productos WHERE tipo_producto = 'HERRAJE') * 100.0 / (SELECT COUNT(*) FROM herrajes))
            ELSE 0
        END;
END

-- Insertar estadísticas de vidrios
IF EXISTS (SELECT * FROM sysobjects WHERE name='vidrios' AND xtype='U')
BEGIN
    INSERT INTO temp_migracion_summary (tabla_origen, registros_origen, registros_migrados, porcentaje_migracion)
    SELECT 
        'vidrios',
        (SELECT COUNT(*) FROM vidrios),
        (SELECT COUNT(*) FROM productos WHERE tipo_producto = 'VIDRIO'),
        CASE 
            WHEN (SELECT COUNT(*) FROM vidrios) > 0 
            THEN ((SELECT COUNT(*) FROM productos WHERE tipo_producto = 'VIDRIO') * 100.0 / (SELECT COUNT(*) FROM vidrios))
            ELSE 0
        END;
END

-- Mostrar resumen final
SELECT * FROM temp_migracion_summary;

-- =====================================================================
-- 8. FINALIZACIÓN Y RECOMENDACIONES
-- =====================================================================

PRINT '';
PRINT '========================================';
PRINT 'MIGRACIÓN COMPLETADA EXITOSAMENTE';
PRINT '========================================';
PRINT '';
PRINT 'PRÓXIMOS PASOS RECOMENDADOS:';
PRINT '1. Verificar que los datos migrados son correctos';
PRINT '2. Actualizar el código de la aplicación para usar la tabla productos';
PRINT '3. Crear backup de las tablas originales';
PRINT '4. Probar la aplicación con la nueva estructura';
PRINT '5. Una vez validado, eliminar tablas antiguas (inventario, herrajes, vidrios)';
PRINT '';
PRINT 'TABLAS DE RESPALDO CREADAS:';
PRINT '- temp_migracion_summary (estadísticas de migración)';
PRINT '';
PRINT 'ADVERTENCIAS:';
PRINT '- No elimine las tablas originales hasta validar completamente';
PRINT '- Actualice las referencias en el código de la aplicación';
PRINT '- Verifique que las vistas de compatibilidad funcionen correctamente';
PRINT '========================================';