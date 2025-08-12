-- =====================================================
-- FASE 1.4: Migrar datos de vidrios a productos
-- Categoría: VIDRIO
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO MIGRACIÓN: vidrios → productos ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Verificar que la tabla productos existe
IF OBJECT_ID('productos', 'U') IS NULL
BEGIN
    PRINT 'ERROR: La tabla productos no existe. Ejecute primero 01_crear_tabla_productos.sql';
    RETURN;
END

-- Verificar que la tabla vidrios existe
IF OBJECT_ID('vidrios', 'U') IS NULL
BEGIN
    PRINT 'WARNING: La tabla vidrios no existe. Saltando migración.';
    RETURN;
END

-- Contar registros a migrar
DECLARE @total_registros INT;
SELECT @total_registros = COUNT(*) FROM vidrios WHERE activo = 1;
PRINT 'Registros a migrar: ' + CAST(@total_registros AS VARCHAR);

-- Verificar si ya hay datos migrados
DECLARE @ya_migrados INT;
SELECT @ya_migrados = COUNT(*) FROM productos WHERE categoria = 'VIDRIO';
IF @ya_migrados > 0
BEGIN
    PRINT 'WARNING: Ya existen ' + CAST(@ya_migrados AS VARCHAR) + ' productos con categoría VIDRIO';
    PRINT 'Continuando con migración incremental...';
END

PRINT '';
PRINT 'Iniciando migración de datos...';

-- Iniciar transacción
BEGIN TRANSACTION MigrarVidrios;

BEGIN TRY
    -- Migrar datos de vidrios a productos
    INSERT INTO productos (
        codigo, descripcion, categoria, subcategoria, tipo,
        stock_actual, stock_minimo, stock_maximo, stock_reservado,
        precio_unitario, precio_promedio, costo_unitario,
        unidad_medida, ubicacion, dimensiones, peso, color, material, marca, modelo, acabado,
        proveedor, codigo_proveedor, tiempo_entrega_dias,
        propiedades_adicionales, especificaciones, observaciones,
        codigo_qr, imagen_url, codigo_barras,
        es_critico, permite_reserva, requiere_aprobacion,
        estado, activo, fecha_creacion, fecha_actualizacion,
        usuario_creacion, usuario_modificacion, version
    )
    SELECT 
        -- Identificación básica
        ISNULL(v.codigo, 'VID-' + CAST(v.id AS VARCHAR)) as codigo,
        ISNULL(v.descripcion, v.tipo + ' de ' + CAST(v.espesor AS VARCHAR) + 'mm') as descripcion,
        'VIDRIO' as categoria,
        ISNULL(v.tipo, 'TRANSPARENTE') as subcategoria,
        CASE 
            WHEN v.templado = 1 THEN 'TEMPLADO'
            WHEN v.laminado = 1 THEN 'LAMINADO'
            WHEN v.doble_vidriado_hermetico = 1 THEN 'DVH'
            ELSE ISNULL(v.categoria, 'SIMPLE')
        END as tipo,
        
        -- Stock (vidrios suelen manejarse por m²)
        ISNULL(v.stock_m2, 0) as stock_actual,
        ISNULL(v.stock_minimo, 20) as stock_minimo, -- 20 m² mínimo típico
        ISNULL(v.stock_maximo, 1000) as stock_maximo, 
        0 as stock_reservado, -- Inicializar en 0
        
        -- Precios (por m²)
        ISNULL(v.precio_m2, 0) as precio_unitario,
        ISNULL(v.precio_compra, v.precio_m2) as precio_promedio,
        ISNULL(v.costo_m2, v.precio_m2 * 0.7) as costo_unitario, -- Estimado 70% del precio
        
        -- Propiedades físicas
        'M2' as unidad_medida, -- Vidrios se miden en metros cuadrados
        v.ubicacion,
        CASE 
            WHEN v.largo_max IS NOT NULL AND v.ancho_max IS NOT NULL 
            THEN 'Max: ' + CAST(v.largo_max AS VARCHAR) + ' x ' + CAST(v.ancho_max AS VARCHAR) + ' x ' + CAST(v.espesor AS VARCHAR) + 'mm'
            WHEN v.espesor IS NOT NULL
            THEN 'Espesor: ' + CAST(v.espesor AS VARCHAR) + 'mm'
            ELSE NULL
        END as dimensiones,
        CAST(v.espesor * 2.5 AS DECIMAL(10,3)) as peso, -- Estimado: 2.5kg por mm de espesor por m²
        ISNULL(v.color, 'TRANSPARENTE') as color,
        'VIDRIO' as material,
        v.marca,
        v.modelo,
        CASE 
            WHEN v.templado = 1 AND v.laminado = 1 THEN 'TEMPLADO-LAMINADO'
            WHEN v.templado = 1 THEN 'TEMPLADO'
            WHEN v.laminado = 1 THEN 'LAMINADO'
            WHEN v.doble_vidriado_hermetico = 1 THEN 'DVH'
            ELSE 'PULIDO'
        END as acabado,
        
        -- Proveedor
        v.proveedor,
        v.codigo_proveedor,
        ISNULL(v.tiempo_entrega, 10) as tiempo_entrega_dias, -- Default 10 días para vidrios
        
        -- Datos adicionales (características específicas de vidrios)
        CASE 
            WHEN v.espesor IS NOT NULL OR v.templado IS NOT NULL OR v.laminado IS NOT NULL
            THEN '{"espesor":' + CAST(ISNULL(v.espesor, 0) AS VARCHAR) + 
                 ',"templado":' + CAST(ISNULL(v.templado, 0) AS VARCHAR) + 
                 ',"laminado":' + CAST(ISNULL(v.laminado, 0) AS VARCHAR) + 
                 ',"dvh":' + CAST(ISNULL(v.doble_vidriado_hermetico, 0) AS VARCHAR) + 
                 ',"transmitancia_termica":"' + ISNULL(v.transmitancia_termica, '') + 
                 '","factor_solar":"' + ISNULL(v.factor_solar, '') + 
                 '","resistencia_viento":"' + ISNULL(v.resistencia_viento, '') + '"}'
            ELSE NULL
        END as propiedades_adicionales,
        ISNULL(v.especificaciones, v.ficha_tecnica) as especificaciones,
        v.observaciones,
        
        -- Códigos
        v.codigo_qr,
        v.imagen_url,
        v.codigo_barras,
        
        -- Reglas de negocio (vidrios de seguridad y estructurales son críticos)
        CASE 
            WHEN v.templado = 1 OR v.laminado = 1 OR v.tipo IN ('SEGURIDAD', 'ESTRUCTURAL') THEN 1 
            ELSE 0 
        END as es_critico,
        1 as permite_reserva, -- Por defecto permitir reservas
        CASE WHEN v.precio_m2 > 8000 THEN 1 ELSE 0 END as requiere_aprobacion, -- Vidrios especiales
        
        -- Control
        CASE 
            WHEN v.activo = 1 AND ISNULL(v.stock_m2, 0) >= 0 THEN 'ACTIVO'
            WHEN v.activo = 0 THEN 'INACTIVO'
            WHEN v.estado = 'DESCONTINUADO' THEN 'DESCONTINUADO'
            ELSE 'ACTIVO'
        END as estado,
        ISNULL(v.activo, 1) as activo,
        ISNULL(v.fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(v.fecha_actualizacion, GETDATE()) as fecha_actualizacion,
        ISNULL(v.usuario_creacion, 'MIGRACION') as usuario_creacion,
        ISNULL(v.usuario_modificacion, 'MIGRACION') as usuario_modificacion,
        1 as version
        
    FROM vidrios v
    WHERE v.activo = 1 
        AND NOT EXISTS (
            SELECT 1 FROM productos p 
            WHERE p.codigo = ISNULL(v.codigo, 'VID-' + CAST(v.id AS VARCHAR))
        );

    -- Obtener estadísticas de migración
    DECLARE @migrados INT;
    SELECT @migrados = @@ROWCOUNT;
    
    PRINT 'Registros migrados exitosamente: ' + CAST(@migrados AS VARCHAR);
    
    -- Verificar integridad de datos migrados
    DECLARE @errores INT = 0;
    
    -- Verificar códigos únicos
    IF EXISTS (SELECT codigo FROM productos WHERE categoria = 'VIDRIO' GROUP BY codigo HAVING COUNT(*) > 1)
    BEGIN
        PRINT 'ERROR: Códigos duplicados detectados en productos VIDRIO';
        SET @errores = @errores + 1;
    END
    
    -- Verificar stock negativo
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'VIDRIO' AND stock_actual < 0)
    BEGIN
        PRINT 'ERROR: Stock negativo detectado en productos VIDRIO';
        SET @errores = @errores + 1;
    END
    
    -- Verificar precios negativos
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'VIDRIO' AND precio_unitario < 0)
    BEGIN
        PRINT 'ERROR: Precios negativos detectados en productos VIDRIO';
        SET @errores = @errores + 1;
    END
    
    IF @errores > 0
    BEGIN
        PRINT 'Se encontraron ' + CAST(@errores AS VARCHAR) + ' errores. Abortando migración.';
        ROLLBACK TRANSACTION MigrarVidrios;
        RETURN;
    END
    
    -- Actualizar estadísticas
    UPDATE STATISTICS productos;
    
    -- Insertar mapeo en tabla de referencia
    INSERT INTO mapeo_inventario_productos (id_original, tabla_original, id_nuevo, codigo_nuevo)
    SELECT 
        v.id,
        'vidrios',
        p.id,
        p.codigo
    FROM vidrios v
    INNER JOIN productos p ON p.codigo = ISNULL(v.codigo, 'VID-' + CAST(v.id AS VARCHAR))
    WHERE p.categoria = 'VIDRIO'
        AND NOT EXISTS (
            SELECT 1 FROM mapeo_inventario_productos m 
            WHERE m.id_original = v.id AND m.tabla_original = 'vidrios'
        );
    
    -- Confirmar transacción
    COMMIT TRANSACTION MigrarVidrios;
    
    PRINT '';
    PRINT '=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===';
    PRINT 'Total de vidrios migrados: ' + CAST(@migrados AS VARCHAR);
    
    -- Mostrar estadísticas finales por todas las categorías
    SELECT 
        categoria,
        COUNT(*) as total_productos,
        SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
        SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as con_stock_bajo,
        SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as sin_stock,
        CAST(SUM(stock_actual * precio_unitario) AS DECIMAL(18,2)) as valor_inventario,
        CAST(AVG(stock_actual) AS DECIMAL(10,2)) as promedio_stock,
        CAST(AVG(precio_unitario) AS DECIMAL(10,2)) as precio_promedio
    FROM productos 
    WHERE categoria IN ('PERFIL', 'HERRAJE', 'VIDRIO')
    GROUP BY categoria
    ORDER BY categoria;
    
    -- Mostrar resumen total del inventario consolidado
    PRINT '';
    PRINT 'RESUMEN TOTAL DEL INVENTARIO CONSOLIDADO:';
    SELECT 
        COUNT(*) as total_productos,
        SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as productos_activos,
        SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as productos_stock_bajo,
        SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as productos_sin_stock,
        CAST(SUM(stock_actual * precio_unitario) AS DECIMAL(18,2)) as valor_total_inventario,
        CAST(AVG(precio_unitario) AS DECIMAL(10,2)) as precio_promedio_general
    FROM productos 
    WHERE categoria IN ('PERFIL', 'HERRAJE', 'VIDRIO');
    
    -- Mostrar productos más valiosos con stock bajo
    PRINT '';
    PRINT 'Top 10 productos más valiosos con stock bajo:';
    SELECT TOP 10
        categoria, codigo, descripcion, tipo, 
        stock_actual, stock_minimo, precio_unitario,
        (stock_minimo - stock_actual) as deficit,
        CAST(stock_actual * precio_unitario AS DECIMAL(10,2)) as valor_actual,
        CAST((stock_minimo - stock_actual) * precio_unitario AS DECIMAL(10,2)) as valor_deficit
    FROM productos 
    WHERE categoria IN ('PERFIL', 'HERRAJE', 'VIDRIO')
        AND stock_actual <= stock_minimo
        AND precio_unitario > 0
    ORDER BY valor_deficit DESC;
    
    PRINT '';
    PRINT '=== FASE 1 (INVENTARIO) COMPLETADA ===';
    PRINT 'Próximo paso: Ejecutar 05_crear_tabla_auditoria.sql';
    
END TRY
BEGIN CATCH
    -- Error en la migración
    ROLLBACK TRANSACTION MigrarVidrios;
    
    PRINT '';
    PRINT '=== ERROR EN LA MIGRACIÓN ===';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT '';
    PRINT 'La migración ha sido revertida. Revise los errores y vuelva a intentar.';
    
END CATCH

GO