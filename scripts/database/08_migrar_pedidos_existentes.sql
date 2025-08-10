-- =====================================================
-- FASE 2.2: Migrar pedidos existentes al sistema consolidado
-- Migra: pedidos, pedidos_compra, compras y sus detalles
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO MIGRACIÓN: Pedidos existentes → sistema consolidado ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Verificar que las tablas consolidadas existen
IF OBJECT_ID('pedidos_consolidado', 'U') IS NULL OR OBJECT_ID('pedidos_detalle_consolidado', 'U') IS NULL
BEGIN
    PRINT 'ERROR: Las tablas consolidadas no existen. Ejecute primero 07_crear_sistema_pedidos.sql';
    RETURN;
END

-- Verificar que la tabla productos existe
IF OBJECT_ID('productos', 'U') IS NULL
BEGIN
    PRINT 'ERROR: La tabla productos no existe. Complete primero la migración de inventario.';
    RETURN;
END

-- Contar registros a migrar
DECLARE @total_pedidos INT = 0;
DECLARE @total_detalles INT = 0;

SELECT @total_pedidos = 
    ISNULL((SELECT COUNT(*) FROM pedidos WHERE activo = 1), 0) +
    ISNULL((SELECT COUNT(*) FROM pedidos_compra WHERE activo = 1), 0) +
    ISNULL((SELECT COUNT(*) FROM compras WHERE activo = 1), 0);

SELECT @total_detalles = 
    ISNULL((SELECT COUNT(*) FROM pedidos_detalle pd INNER JOIN pedidos p ON pd.pedido_id = p.id WHERE p.activo = 1), 0) +
    ISNULL((SELECT COUNT(*) FROM detalle_pedido dp INNER JOIN pedidos_compra pc ON dp.pedido_id = pc.id WHERE pc.activo = 1), 0) +
    ISNULL((SELECT COUNT(*) FROM detalle_compras dc INNER JOIN compras c ON dc.compra_id = c.id WHERE c.activo = 1), 0);

PRINT 'Pedidos a migrar: ' + CAST(@total_pedidos AS VARCHAR);
PRINT 'Detalles a migrar: ' + CAST(@total_detalles AS VARCHAR);
PRINT '';

-- Iniciar transacción
BEGIN TRANSACTION MigrarPedidos;

BEGIN TRY
    -- ========================================================
    -- MIGRAR TABLA: pedidos (Pedidos de venta/obra)
    -- ========================================================
    IF OBJECT_ID('pedidos', 'U') IS NOT NULL
    BEGIN
        PRINT 'Migrando pedidos de venta/obra...';
        
        INSERT INTO pedidos_consolidado (
            numero_pedido, obra_id, tipo_pedido, categoria_pedido, estado, prioridad,
            fecha_pedido, fecha_entrega_solicitada, 
            subtotal, descuento_monto, impuestos_monto, total, moneda,
            direccion_entrega, contacto_entrega, telefono_contacto,
            observaciones, usuario_creador, fecha_creacion, activo
        )
        SELECT 
            ISNULL(p.numero_pedido, 'PED-' + CAST(p.id AS VARCHAR)) as numero_pedido,
            p.obra_id,
            CASE 
                WHEN p.obra_id IS NOT NULL THEN 'OBRA'
                ELSE 'VENTA'
            END as tipo_pedido,
            'MIXTO' as categoria_pedido, -- Se determinará después por los detalles
            
            CASE 
                WHEN UPPER(p.estado) = 'PENDIENTE' THEN 'PENDIENTE'
                WHEN UPPER(p.estado) = 'APROBADO' THEN 'APROBADO'
                WHEN UPPER(p.estado) = 'EN_PROCESO' THEN 'EN_PROCESO'
                WHEN UPPER(p.estado) = 'ENTREGADO' THEN 'ENTREGADO'
                WHEN UPPER(p.estado) = 'CANCELADO' THEN 'CANCELADO'
                WHEN UPPER(p.estado) = 'BORRADOR' THEN 'BORRADOR'
                ELSE 'PENDIENTE'
            END as estado,
            
            CASE 
                WHEN UPPER(p.prioridad) = 'ALTA' THEN 'ALTA'
                WHEN UPPER(p.prioridad) = 'URGENTE' THEN 'URGENTE'
                WHEN UPPER(p.prioridad) = 'BAJA' THEN 'BAJA'
                ELSE 'NORMAL'
            END as prioridad,
            
            ISNULL(p.fecha_pedido, p.fecha_creacion) as fecha_pedido,
            p.fecha_entrega as fecha_entrega_solicitada,
            
            ISNULL(p.subtotal, 0) as subtotal,
            ISNULL(p.descuento, 0) as descuento_monto,
            ISNULL(p.impuestos, 0) as impuestos_monto,
            ISNULL(p.total, 0) as total,
            ISNULL(p.moneda, 'ARS') as moneda,
            
            p.direccion_entrega,
            p.contacto_entrega,
            p.telefono_entrega as telefono_contacto,
            p.observaciones,
            ISNULL(p.usuario_creador, 1) as usuario_creador, -- Default usuario 1 si no existe
            ISNULL(p.fecha_creacion, GETDATE()) as fecha_creacion,
            ISNULL(p.activo, 1) as activo
            
        FROM pedidos p
        WHERE p.activo = 1
            AND NOT EXISTS (
                SELECT 1 FROM pedidos_consolidado pc 
                WHERE pc.numero_pedido = ISNULL(p.numero_pedido, 'PED-' + CAST(p.id AS VARCHAR))
            );
        
        DECLARE @migrados_pedidos INT = @@ROWCOUNT;
        PRINT 'Pedidos de venta/obra migrados: ' + CAST(@migrados_pedidos AS VARCHAR);
        
        -- Migrar detalles de pedidos
        INSERT INTO pedidos_detalle_consolidado (
            pedido_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
            cantidad, cantidad_entregada, unidad_medida, precio_unitario, subtotal_item,
            observaciones_item, fecha_creacion, activo, numero_linea
        )
        SELECT 
            pc.id as pedido_id,
            COALESCE(prod.id, 
                -- Si no encuentra el producto, crear una entrada genérica
                (SELECT TOP 1 id FROM productos WHERE codigo LIKE '%GENERICO%' OR descripcion LIKE '%GENERICO%')
            ) as producto_id,
            ISNULL(pd.codigo_producto, 'SIN-CODIGO-' + CAST(pd.id AS VARCHAR)) as codigo_producto,
            ISNULL(pd.descripcion, 'Producto sin descripción') as descripcion_producto,
            ISNULL(prod.categoria, 'MATERIAL') as categoria_producto,
            
            ISNULL(pd.cantidad, 1) as cantidad,
            ISNULL(pd.cantidad_entregada, 0) as cantidad_entregada,
            ISNULL(pd.unidad_medida, 'UND') as unidad_medida,
            ISNULL(pd.precio_unitario, 0) as precio_unitario,
            ISNULL(pd.subtotal, pd.cantidad * pd.precio_unitario) as subtotal_item,
            
            pd.observaciones as observaciones_item,
            ISNULL(pd.fecha_creacion, pc.fecha_creacion) as fecha_creacion,
            1 as activo,
            ISNULL(pd.numero_linea, ROW_NUMBER() OVER (PARTITION BY pd.pedido_id ORDER BY pd.id)) as numero_linea
            
        FROM pedidos_detalle pd
        INNER JOIN pedidos p ON pd.pedido_id = p.id
        INNER JOIN pedidos_consolidado pc ON pc.numero_pedido = ISNULL(p.numero_pedido, 'PED-' + CAST(p.id AS VARCHAR))
        LEFT JOIN productos prod ON (
            prod.codigo = pd.codigo_producto OR 
            prod.descripcion = pd.descripcion OR
            (prod.codigo LIKE '%' + SUBSTRING(pd.codigo_producto, 1, 10) + '%' AND pd.codigo_producto IS NOT NULL)
        )
        WHERE p.activo = 1;
        
        DECLARE @migrados_detalle_pedidos INT = @@ROWCOUNT;
        PRINT 'Detalles de pedidos migrados: ' + CAST(@migrados_detalle_pedidos AS VARCHAR);
        
        -- Crear mapeo para referencia futura
        IF OBJECT_ID('mapeo_pedidos', 'U') IS NULL
        BEGIN
            CREATE TABLE mapeo_pedidos (
                id_original INT,
                tabla_original NVARCHAR(50),
                id_nuevo INT,
                numero_nuevo NVARCHAR(50),
                fecha_migracion DATETIME DEFAULT GETDATE()
            );
        END
        
        INSERT INTO mapeo_pedidos (id_original, tabla_original, id_nuevo, numero_nuevo)
        SELECT p.id, 'pedidos', pc.id, pc.numero_pedido
        FROM pedidos p
        INNER JOIN pedidos_consolidado pc ON pc.numero_pedido = ISNULL(p.numero_pedido, 'PED-' + CAST(p.id AS VARCHAR))
        WHERE NOT EXISTS (SELECT 1 FROM mapeo_pedidos m WHERE m.id_original = p.id AND m.tabla_original = 'pedidos');
    END
    ELSE
    BEGIN
        PRINT 'Tabla pedidos no existe - saltando';
    END

    -- ========================================================
    -- MIGRAR TABLA: pedidos_compra (Órdenes de compra)
    -- ========================================================
    IF OBJECT_ID('pedidos_compra', 'U') IS NOT NULL
    BEGIN
        PRINT '';
        PRINT 'Migrando pedidos de compra...';
        
        INSERT INTO pedidos_consolidado (
            numero_pedido, proveedor_id, tipo_pedido, categoria_pedido, estado, prioridad,
            fecha_pedido, fecha_entrega_solicitada, 
            subtotal, descuento_monto, impuestos_monto, total, moneda,
            observaciones, orden_compra_cliente, usuario_creador, fecha_creacion, activo
        )
        SELECT 
            ISNULL(pc.numero_pedido, 'COMP-' + CAST(pc.id AS VARCHAR)) as numero_pedido,
            pc.proveedor_id,
            'COMPRA' as tipo_pedido,
            'MIXTO' as categoria_pedido,
            
            CASE 
                WHEN UPPER(pc.estado) = 'PENDIENTE' THEN 'PENDIENTE'
                WHEN UPPER(pc.estado) = 'APROBADO' THEN 'APROBADO'
                WHEN UPPER(pc.estado) = 'RECIBIDO' THEN 'ENTREGADO'
                WHEN UPPER(pc.estado) = 'CANCELADO' THEN 'CANCELADO'
                ELSE 'PENDIENTE'
            END as estado,
            
            CASE 
                WHEN UPPER(pc.urgencia) = 'ALTA' THEN 'ALTA'
                WHEN UPPER(pc.urgencia) = 'URGENTE' THEN 'URGENTE'
                ELSE 'NORMAL'
            END as prioridad,
            
            ISNULL(pc.fecha_pedido, pc.fecha_creacion) as fecha_pedido,
            pc.fecha_entrega_esperada as fecha_entrega_solicitada,
            
            ISNULL(pc.subtotal, 0) as subtotal,
            ISNULL(pc.descuento, 0) as descuento_monto,
            ISNULL(pc.iva, 0) as impuestos_monto,
            ISNULL(pc.total, 0) as total,
            'ARS' as moneda,
            
            pc.observaciones,
            pc.numero_orden_compra as orden_compra_cliente,
            ISNULL(pc.usuario_creador, 1) as usuario_creador,
            ISNULL(pc.fecha_creacion, GETDATE()) as fecha_creacion,
            ISNULL(pc.activo, 1) as activo
            
        FROM pedidos_compra pc
        WHERE pc.activo = 1
            AND NOT EXISTS (
                SELECT 1 FROM pedidos_consolidado pcon 
                WHERE pcon.numero_pedido = ISNULL(pc.numero_pedido, 'COMP-' + CAST(pc.id AS VARCHAR))
            );
        
        DECLARE @migrados_compras INT = @@ROWCOUNT;
        PRINT 'Pedidos de compra migrados: ' + CAST(@migrados_compras AS VARCHAR);
        
        -- Migrar detalles de pedidos_compra
        INSERT INTO pedidos_detalle_consolidado (
            pedido_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
            cantidad, cantidad_entregada, unidad_medida, precio_unitario, subtotal_item,
            observaciones_item, fecha_creacion, activo, numero_linea
        )
        SELECT 
            pcon.id as pedido_id,
            COALESCE(prod.id, 
                (SELECT TOP 1 id FROM productos WHERE codigo LIKE '%GENERICO%' OR descripcion LIKE '%GENERICO%')
            ) as producto_id,
            ISNULL(dp.codigo_producto, 'SIN-CODIGO-' + CAST(dp.id AS VARCHAR)) as codigo_producto,
            ISNULL(dp.descripcion, 'Producto sin descripción') as descripcion_producto,
            ISNULL(prod.categoria, 'MATERIAL') as categoria_producto,
            
            ISNULL(dp.cantidad, 1) as cantidad,
            ISNULL(dp.cantidad_recibida, 0) as cantidad_entregada,
            ISNULL(dp.unidad, 'UND') as unidad_medida,
            ISNULL(dp.precio_unitario, 0) as precio_unitario,
            ISNULL(dp.subtotal, dp.cantidad * dp.precio_unitario) as subtotal_item,
            
            dp.observaciones as observaciones_item,
            ISNULL(dp.fecha_creacion, pcon.fecha_creacion) as fecha_creacion,
            1 as activo,
            ROW_NUMBER() OVER (PARTITION BY dp.pedido_id ORDER BY dp.id) as numero_linea
            
        FROM detalle_pedido dp
        INNER JOIN pedidos_compra pc ON dp.pedido_id = pc.id
        INNER JOIN pedidos_consolidado pcon ON pcon.numero_pedido = ISNULL(pc.numero_pedido, 'COMP-' + CAST(pc.id AS VARCHAR))
        LEFT JOIN productos prod ON (
            prod.codigo = dp.codigo_producto OR 
            prod.descripcion = dp.descripcion OR
            (prod.codigo LIKE '%' + SUBSTRING(dp.codigo_producto, 1, 10) + '%' AND dp.codigo_producto IS NOT NULL)
        )
        WHERE pc.activo = 1;
        
        DECLARE @migrados_detalle_compras INT = @@ROWCOUNT;
        PRINT 'Detalles de compras migrados: ' + CAST(@migrados_detalle_compras AS VARCHAR);
        
        -- Agregar al mapeo
        INSERT INTO mapeo_pedidos (id_original, tabla_original, id_nuevo, numero_nuevo)
        SELECT pc.id, 'pedidos_compra', pcon.id, pcon.numero_pedido
        FROM pedidos_compra pc
        INNER JOIN pedidos_consolidado pcon ON pcon.numero_pedido = ISNULL(pc.numero_pedido, 'COMP-' + CAST(pc.id AS VARCHAR))
        WHERE NOT EXISTS (SELECT 1 FROM mapeo_pedidos m WHERE m.id_original = pc.id AND m.tabla_original = 'pedidos_compra');
    END
    ELSE
    BEGIN
        PRINT 'Tabla pedidos_compra no existe - saltando';
    END

    -- ========================================================
    -- MIGRAR TABLA: compras (Sistema de compras alternativo)
    -- ========================================================
    IF OBJECT_ID('compras', 'U') IS NOT NULL
    BEGIN
        PRINT '';
        PRINT 'Migrando sistema de compras alternativo...';
        
        INSERT INTO pedidos_consolidado (
            numero_pedido, tipo_pedido, categoria_pedido, estado, prioridad,
            fecha_pedido, fecha_entrega_solicitada, 
            subtotal, total, moneda, observaciones, usuario_creador, fecha_creacion, activo
        )
        SELECT 
            ISNULL(c.numero_compra, 'COMPRA-' + CAST(c.id AS VARCHAR)) as numero_pedido,
            'COMPRA' as tipo_pedido,
            'MIXTO' as categoria_pedido,
            
            CASE 
                WHEN UPPER(c.estado) = 'PENDIENTE' THEN 'PENDIENTE'
                WHEN UPPER(c.estado) = 'PROCESADA' THEN 'EN_PROCESO'
                WHEN UPPER(c.estado) = 'COMPLETADA' THEN 'ENTREGADO'
                WHEN UPPER(c.estado) = 'CANCELADA' THEN 'CANCELADO'
                ELSE 'PENDIENTE'
            END as estado,
            
            'NORMAL' as prioridad,
            ISNULL(c.fecha_compra, c.fecha_creacion) as fecha_pedido,
            c.fecha_entrega_esperada as fecha_entrega_solicitada,
            
            ISNULL(c.subtotal, 0) as subtotal,
            ISNULL(c.total, 0) as total,
            'ARS' as moneda,
            c.observaciones,
            ISNULL(c.usuario_creador, 1) as usuario_creador,
            ISNULL(c.fecha_creacion, GETDATE()) as fecha_creacion,
            ISNULL(c.activo, 1) as activo
            
        FROM compras c
        WHERE c.activo = 1
            AND NOT EXISTS (
                SELECT 1 FROM pedidos_consolidado pcon 
                WHERE pcon.numero_pedido = ISNULL(c.numero_compra, 'COMPRA-' + CAST(c.id AS VARCHAR))
            );
        
        DECLARE @migrados_compras_alt INT = @@ROWCOUNT;
        PRINT 'Compras alternativas migradas: ' + CAST(@migrados_compras_alt AS VARCHAR);
        
        -- Migrar detalles de compras
        IF OBJECT_ID('detalle_compras', 'U') IS NOT NULL
        BEGIN
            INSERT INTO pedidos_detalle_consolidado (
                pedido_id, producto_id, codigo_producto, descripcion_producto, categoria_producto,
                cantidad, unidad_medida, precio_unitario, subtotal_item,
                fecha_creacion, activo, numero_linea
            )
            SELECT 
                pcon.id as pedido_id,
                COALESCE(prod.id, 
                    (SELECT TOP 1 id FROM productos WHERE codigo LIKE '%GENERICO%' OR descripcion LIKE '%GENERICO%')
                ) as producto_id,
                ISNULL(dc.codigo_producto, 'SIN-CODIGO-' + CAST(dc.id AS VARCHAR)) as codigo_producto,
                ISNULL(dc.descripcion, 'Producto sin descripción') as descripcion_producto,
                ISNULL(prod.categoria, 'MATERIAL') as categoria_producto,
                
                ISNULL(dc.cantidad, 1) as cantidad,
                ISNULL(dc.unidad, 'UND') as unidad_medida,
                ISNULL(dc.precio_unitario, 0) as precio_unitario,
                ISNULL(dc.subtotal, dc.cantidad * dc.precio_unitario) as subtotal_item,
                
                ISNULL(dc.fecha_creacion, pcon.fecha_creacion) as fecha_creacion,
                1 as activo,
                ROW_NUMBER() OVER (PARTITION BY dc.compra_id ORDER BY dc.id) as numero_linea
                
            FROM detalle_compras dc
            INNER JOIN compras c ON dc.compra_id = c.id
            INNER JOIN pedidos_consolidado pcon ON pcon.numero_pedido = ISNULL(c.numero_compra, 'COMPRA-' + CAST(c.id AS VARCHAR))
            LEFT JOIN productos prod ON (
                prod.codigo = dc.codigo_producto OR 
                prod.descripcion = dc.descripcion OR
                (prod.codigo LIKE '%' + SUBSTRING(dc.codigo_producto, 1, 10) + '%' AND dc.codigo_producto IS NOT NULL)
            )
            WHERE c.activo = 1;
            
            DECLARE @migrados_detalle_compras_alt INT = @@ROWCOUNT;
            PRINT 'Detalles de compras alternativas migrados: ' + CAST(@migrados_detalle_compras_alt AS VARCHAR);
        END
        
        -- Agregar al mapeo
        INSERT INTO mapeo_pedidos (id_original, tabla_original, id_nuevo, numero_nuevo)
        SELECT c.id, 'compras', pcon.id, pcon.numero_pedido
        FROM compras c
        INNER JOIN pedidos_consolidado pcon ON pcon.numero_pedido = ISNULL(c.numero_compra, 'COMPRA-' + CAST(c.id AS VARCHAR))
        WHERE NOT EXISTS (SELECT 1 FROM mapeo_pedidos m WHERE m.id_original = c.id AND m.tabla_original = 'compras');
    END
    ELSE
    BEGIN
        PRINT 'Tabla compras no existe - saltando';
    END

    -- ========================================================
    -- ACTUALIZAR CATEGORÍAS DE PEDIDOS BASADO EN PRODUCTOS
    -- ========================================================
    PRINT '';
    PRINT 'Actualizando categorías de pedidos basado en productos...';
    
    UPDATE pc SET categoria_pedido = 
        CASE 
            WHEN cat_stats.cat_count = 1 THEN cat_stats.categoria_principal
            ELSE 'MIXTO'
        END
    FROM pedidos_consolidado pc
    INNER JOIN (
        SELECT 
            pd.pedido_id,
            COUNT(DISTINCT pd.categoria_producto) as cat_count,
            (SELECT TOP 1 pd2.categoria_producto 
             FROM pedidos_detalle_consolidado pd2 
             WHERE pd2.pedido_id = pd.pedido_id 
             GROUP BY pd2.categoria_producto 
             ORDER BY COUNT(*) DESC) as categoria_principal
        FROM pedidos_detalle_consolidado pd
        WHERE pd.activo = 1
        GROUP BY pd.pedido_id
    ) cat_stats ON pc.id = cat_stats.pedido_id;
    
    PRINT 'Categorías de pedidos actualizadas';

    -- ========================================================
    -- VERIFICACIÓN DE INTEGRIDAD
    -- ========================================================
    PRINT '';
    PRINT 'Verificando integridad de datos migrados...';
    
    DECLARE @errores INT = 0;
    
    -- Verificar números de pedido únicos
    IF EXISTS (SELECT numero_pedido FROM pedidos_consolidado GROUP BY numero_pedido HAVING COUNT(*) > 1)
    BEGIN
        PRINT 'ERROR: Números de pedido duplicados';
        SET @errores = @errores + 1;
    END
    
    -- Verificar que todos los detalles tienen pedido padre
    IF EXISTS (SELECT * FROM pedidos_detalle_consolidado pd WHERE NOT EXISTS (SELECT 1 FROM pedidos_consolidado pc WHERE pc.id = pd.pedido_id))
    BEGIN
        PRINT 'ERROR: Detalles huérfanos encontrados';
        SET @errores = @errores + 1;
    END
    
    -- Verificar que todos los detalles tienen producto válido
    IF EXISTS (SELECT * FROM pedidos_detalle_consolidado pd WHERE pd.producto_id IS NULL)
    BEGIN
        PRINT 'ERROR: Detalles sin producto encontrados';
        SET @errores = @errores + 1;
    END
    
    IF @errores > 0
    BEGIN
        PRINT 'Se encontraron ' + CAST(@errores AS VARCHAR) + ' errores. Abortando migración.';
        ROLLBACK TRANSACTION MigrarPedidos;
        RETURN;
    END
    
    -- Actualizar estadísticas
    UPDATE STATISTICS pedidos_consolidado;
    UPDATE STATISTICS pedidos_detalle_consolidado;
    
    -- Confirmar transacción
    COMMIT TRANSACTION MigrarPedidos;
    
    PRINT '';
    PRINT '=== MIGRACIÓN DE PEDIDOS COMPLETADA EXITOSAMENTE ===';
    
    -- Mostrar estadísticas finales
    SELECT 
        tipo_pedido,
        categoria_pedido,
        COUNT(*) as total_pedidos,
        SUM(CASE WHEN estado = 'PENDIENTE' THEN 1 ELSE 0 END) as pendientes,
        SUM(CASE WHEN estado = 'APROBADO' THEN 1 ELSE 0 END) as aprobados,
        SUM(CASE WHEN estado = 'ENTREGADO' THEN 1 ELSE 0 END) as entregados,
        CAST(SUM(total) AS DECIMAL(18,2)) as valor_total
    FROM pedidos_consolidado
    WHERE activo = 1
    GROUP BY tipo_pedido, categoria_pedido
    ORDER BY tipo_pedido, categoria_pedido;
    
    PRINT '';
    PRINT 'Próximo paso: Ejecutar 09_crear_productos_obra.sql';
    
END TRY
BEGIN CATCH
    -- Error en la migración
    ROLLBACK TRANSACTION MigrarPedidos;
    
    PRINT '';
    PRINT '=== ERROR EN LA MIGRACIÓN ===';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT '';
    PRINT 'La migración ha sido revertida. Revise los errores y vuelva a intentar.';
    
END CATCH

GO