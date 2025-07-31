-- =====================================================
-- FASE 1.3: Migrar datos de herrajes a productos
-- Categoría: HERRAJE
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO MIGRACIÓN: herrajes → productos ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Verificar que la tabla productos existe
IF OBJECT_ID('productos', 'U') IS NULL
BEGIN
    PRINT 'ERROR: La tabla productos no existe. Ejecute primero 01_crear_tabla_productos.sql';
    RETURN;
END

-- Verificar que la tabla herrajes existe
IF OBJECT_ID('herrajes', 'U') IS NULL
BEGIN
    PRINT 'WARNING: La tabla herrajes no existe. Saltando migración.';
    RETURN;
END

-- Contar registros a migrar
DECLARE @total_registros INT;
SELECT @total_registros = COUNT(*) FROM herrajes WHERE activo = 1;
PRINT 'Registros a migrar: ' + CAST(@total_registros AS VARCHAR);

-- Verificar si ya hay datos migrados
DECLARE @ya_migrados INT;
SELECT @ya_migrados = COUNT(*) FROM productos WHERE categoria = 'HERRAJE';
IF @ya_migrados > 0
BEGIN
    PRINT 'WARNING: Ya existen ' + CAST(@ya_migrados AS VARCHAR) + ' productos con categoría HERRAJE';
    PRINT 'Continuando con migración incremental...';
END

PRINT '';
PRINT 'Iniciando migración de datos...';

-- Iniciar transacción
BEGIN TRANSACTION MigrarHerrajes;

BEGIN TRY
    -- Migrar datos de herrajes a productos
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
        ISNULL(h.codigo, 'HERR-' + CAST(h.id AS VARCHAR)) as codigo,
        ISNULL(h.descripcion, 'Herraje sin descripción') as descripcion,
        'HERRAJE' as categoria,
        ISNULL(h.tipo, 'GENERICO') as subcategoria,
        ISNULL(h.subtipo, h.tipo) as tipo,
        
        -- Stock
        ISNULL(h.stock_actual, 0) as stock_actual,
        ISNULL(h.stock_minimo, 5) as stock_minimo, -- Herrajes suelen tener stock mínimo menor
        ISNULL(h.stock_maximo, 500) as stock_maximo, -- Herrajes suelen ocupar menos espacio
        0 as stock_reservado, -- Inicializar en 0
        
        -- Precios
        ISNULL(h.precio_unitario, 0) as precio_unitario,
        ISNULL(h.precio_compra, h.precio_unitario) as precio_promedio,
        ISNULL(h.costo, h.precio_unitario * 0.6) as costo_unitario, -- Estimado 60% del precio
        
        -- Propiedades físicas
        ISNULL(h.unidad_medida, 'UND') as unidad_medida, -- Herrajes suelen ser por unidad
        h.ubicacion,
        CASE 
            WHEN h.medidas IS NOT NULL THEN h.medidas
            WHEN h.largo IS NOT NULL AND h.ancho IS NOT NULL 
            THEN CAST(h.largo AS VARCHAR) + ' x ' + CAST(h.ancho AS VARCHAR) + ' mm'
            ELSE NULL
        END as dimensiones,
        h.peso,
        h.color,
        ISNULL(h.material, 'METAL') as material, -- Herrajes suelen ser metálicos
        h.marca,
        h.modelo,
        h.acabado,
        
        -- Proveedor
        h.proveedor,
        h.codigo_proveedor,
        ISNULL(h.tiempo_entrega, 7) as tiempo_entrega_dias, -- Default 7 días
        
        -- Datos adicionales (convertir a JSON características específicas de herrajes)
        CASE 
            WHEN h.tipo_fijacion IS NOT NULL OR h.resistencia IS NOT NULL OR h.certificacion IS NOT NULL
            THEN '{"tipo_fijacion":"' + ISNULL(h.tipo_fijacion, '') + 
                 '","resistencia":"' + ISNULL(h.resistencia, '') + 
                 '","certificacion":"' + ISNULL(h.certificacion, '') + 
                 '","uso_recomendado":"' + ISNULL(h.uso_recomendado, '') + '"}'
            ELSE NULL
        END as propiedades_adicionales,
        ISNULL(h.especificaciones, h.ficha_tecnica) as especificaciones,
        h.observaciones,
        
        -- Códigos
        h.codigo_qr,
        h.imagen_url,
        h.codigo_barras,
        
        -- Reglas de negocio (herrajes críticos son estructurales)
        CASE WHEN h.tipo IN ('BISAGRA', 'CERRADURA', 'PESTILLO', 'ESTRUCTURAL') THEN 1 ELSE 0 END as es_critico,
        1 as permite_reserva, -- Por defecto permitir reservas
        CASE WHEN h.precio_unitario > 5000 THEN 1 ELSE 0 END as requiere_aprobacion, -- Umbral menor para herrajes
        
        -- Control
        CASE 
            WHEN h.activo = 1 AND ISNULL(h.stock_actual, 0) >= 0 THEN 'ACTIVO'
            WHEN h.activo = 0 THEN 'INACTIVO'
            WHEN h.estado = 'DESCONTINUADO' THEN 'DESCONTINUADO'
            ELSE 'ACTIVO'
        END as estado,
        ISNULL(h.activo, 1) as activo,
        ISNULL(h.fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(h.fecha_actualizacion, GETDATE()) as fecha_actualizacion,
        ISNULL(h.usuario_creacion, 'MIGRACION') as usuario_creacion,
        ISNULL(h.usuario_modificacion, 'MIGRACION') as usuario_modificacion,
        1 as version
        
    FROM herrajes h
    WHERE h.activo = 1 
        AND NOT EXISTS (
            SELECT 1 FROM productos p 
            WHERE p.codigo = ISNULL(h.codigo, 'HERR-' + CAST(h.id AS VARCHAR))
        );

    -- Obtener estadísticas de migración
    DECLARE @migrados INT;
    SELECT @migrados = @@ROWCOUNT;
    
    PRINT 'Registros migrados exitosamente: ' + CAST(@migrados AS VARCHAR);
    
    -- Verificar integridad de datos migrados
    DECLARE @errores INT = 0;
    
    -- Verificar códigos únicos
    IF EXISTS (SELECT codigo FROM productos WHERE categoria = 'HERRAJE' GROUP BY codigo HAVING COUNT(*) > 1)
    BEGIN
        PRINT 'ERROR: Códigos duplicados detectados en productos HERRAJE';
        SET @errores = @errores + 1;
    END
    
    -- Verificar stock negativo
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'HERRAJE' AND stock_actual < 0)
    BEGIN
        PRINT 'ERROR: Stock negativo detectado en productos HERRAJE';
        SET @errores = @errores + 1;
    END
    
    -- Verificar precios negativos
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'HERRAJE' AND precio_unitario < 0)
    BEGIN
        PRINT 'ERROR: Precios negativos detectados en productos HERRAJE';
        SET @errores = @errores + 1;
    END
    
    IF @errores > 0
    BEGIN
        PRINT 'Se encontraron ' + CAST(@errores AS VARCHAR) + ' errores. Abortando migración.';
        ROLLBACK TRANSACTION MigrarHerrajes;
        RETURN;
    END
    
    -- Actualizar estadísticas
    UPDATE STATISTICS productos;
    
    -- Insertar mapeo en tabla de referencia
    INSERT INTO mapeo_inventario_productos (id_original, tabla_original, id_nuevo, codigo_nuevo)
    SELECT 
        h.id,
        'herrajes',
        p.id,
        p.codigo
    FROM herrajes h
    INNER JOIN productos p ON p.codigo = ISNULL(h.codigo, 'HERR-' + CAST(h.id AS VARCHAR))
    WHERE p.categoria = 'HERRAJE'
        AND NOT EXISTS (
            SELECT 1 FROM mapeo_inventario_productos m 
            WHERE m.id_original = h.id AND m.tabla_original = 'herrajes'
        );
    
    -- Confirmar transacción
    COMMIT TRANSACTION MigrarHerrajes;
    
    PRINT '';
    PRINT '=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===';
    PRINT 'Total de herrajes migrados: ' + CAST(@migrados AS VARCHAR);
    
    -- Mostrar estadísticas finales por categoría
    SELECT 
        categoria,
        COUNT(*) as total_productos,
        SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
        SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as con_stock_bajo,
        SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as sin_stock,
        CAST(SUM(stock_actual * precio_unitario) AS DECIMAL(18,2)) as valor_inventario,
        CAST(AVG(stock_actual) AS DECIMAL(10,2)) as promedio_stock
    FROM productos 
    WHERE categoria IN ('PERFIL', 'HERRAJE')
    GROUP BY categoria
    ORDER BY categoria;
    
    -- Mostrar herrajes más críticos (stock bajo y alto valor)
    PRINT '';
    PRINT 'Herrajes críticos con stock bajo:';
    SELECT TOP 10
        codigo, descripcion, tipo, stock_actual, stock_minimo, precio_unitario,
        (stock_minimo - stock_actual) as deficit,
        CAST(stock_actual * precio_unitario AS DECIMAL(10,2)) as valor_actual
    FROM productos 
    WHERE categoria = 'HERRAJE' 
        AND stock_actual <= stock_minimo
        AND precio_unitario > 0
    ORDER BY precio_unitario DESC, deficit DESC;
    
    PRINT '';
    PRINT 'Próximo paso: Ejecutar 04_migrar_vidrios_a_productos.sql';
    
END TRY
BEGIN CATCH
    -- Error en la migración
    ROLLBACK TRANSACTION MigrarHerrajes;
    
    PRINT '';
    PRINT '=== ERROR EN LA MIGRACIÓN ===';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT '';
    PRINT 'La migración ha sido revertida. Revise los errores y vuelva a intentar.';
    
END CATCH

GO