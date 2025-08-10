-- =====================================================
-- FASE 1.2: Migrar datos de inventario_perfiles a productos
-- Categoría: PERFIL
-- =====================================================

USE inventario;
GO

PRINT '=== INICIANDO MIGRACIÓN: inventario_perfiles → productos ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Verificar que la tabla productos existe
IF OBJECT_ID('productos', 'U') IS NULL
BEGIN
    PRINT 'ERROR: La tabla productos no existe. Ejecute primero 01_crear_tabla_productos.sql';
    RETURN;
END

-- Verificar que la tabla inventario_perfiles existe
IF OBJECT_ID('inventario_perfiles', 'U') IS NULL
BEGIN
    PRINT 'WARNING: La tabla inventario_perfiles no existe. Saltando migración.';
    RETURN;
END

-- Contar registros a migrar
DECLARE @total_registros INT;
SELECT @total_registros = COUNT(*) FROM inventario_perfiles WHERE activo = 1;
PRINT 'Registros a migrar: ' + CAST(@total_registros AS VARCHAR);

-- Verificar si ya hay datos migrados
DECLARE @ya_migrados INT;
SELECT @ya_migrados = COUNT(*) FROM productos WHERE categoria = 'PERFIL';
IF @ya_migrados > 0
BEGIN
    PRINT 'WARNING: Ya existen ' + CAST(@ya_migrados AS VARCHAR) + ' productos con categoría PERFIL';
    PRINT 'Continuando con migración incremental...';
END

PRINT '';
PRINT 'Iniciando migración de datos...';

-- Iniciar transacción
BEGIN TRANSACTION MigrarInventario;

BEGIN TRY
    -- Migrar datos de inventario_perfiles a productos
    INSERT INTO productos (
        codigo, descripcion, categoria, subcategoria, tipo,
        stock_actual, stock_minimo, stock_maximo, stock_reservado,
        precio_unitario, precio_promedio, costo_unitario,
        unidad_medida, ubicacion, dimensiones, peso, color, material, marca, modelo, acabado,
        proveedor, codigo_proveedor,
        propiedades_adicionales, especificaciones, observaciones,
        codigo_qr, imagen_url, codigo_barras,
        es_critico, permite_reserva, requiere_aprobacion,
        estado, activo, fecha_creacion, fecha_actualizacion,
        usuario_creacion, usuario_modificacion, version
    )
    SELECT 
        -- Identificación básica
        ISNULL(ip.codigo, 'PERF-' + CAST(ip.id AS VARCHAR)) as codigo,
        ISNULL(ip.descripcion, 'Perfil sin descripción') as descripcion,
        'PERFIL' as categoria,
        ISNULL(ip.tipo, 'GENERICO') as subcategoria,
        ISNULL(ip.acabado, ip.tipo) as tipo,
        
        -- Stock
        ISNULL(ip.stock, 0) as stock_actual,
        ISNULL(ip.stock_minimo, 10) as stock_minimo,
        ISNULL(ip.stock_maximo, 1000) as stock_maximo,
        0 as stock_reservado, -- Inicializar en 0
        
        -- Precios
        ISNULL(ip.precio_unitario, 0) as precio_unitario,
        ISNULL(ip.precio_promedio, ip.precio_unitario) as precio_promedio,
        ISNULL(ip.costo_unitario, ip.precio_unitario * 0.7) as costo_unitario, -- Estimado 70% del precio
        
        -- Propiedades físicas
        ISNULL(ip.unidad_medida, 'MT') as unidad_medida,
        ip.ubicacion,
        CASE 
            WHEN ip.largo IS NOT NULL AND ip.ancho IS NOT NULL 
            THEN CAST(ip.largo AS VARCHAR) + ' x ' + CAST(ip.ancho AS VARCHAR) + ' mm'
            ELSE NULL
        END as dimensiones,
        ip.peso,
        ip.color,
        ISNULL(ip.material, 'ALUMINIO') as material,
        ip.marca,
        ip.modelo,
        ip.acabado,
        
        -- Proveedor
        ip.proveedor,
        ip.codigo_proveedor,
        
        -- Datos adicionales (convertir a JSON si es necesario)
        CASE 
            WHEN ip.largo IS NOT NULL OR ip.ancho IS NOT NULL OR ip.espesor IS NOT NULL
            THEN '{"largo":' + ISNULL(CAST(ip.largo AS VARCHAR), 'null') + 
                 ',"ancho":' + ISNULL(CAST(ip.ancho AS VARCHAR), 'null') + 
                 ',"espesor":' + ISNULL(CAST(ip.espesor AS VARCHAR), 'null') + '}'
            ELSE NULL
        END as propiedades_adicionales,
        ip.especificaciones,
        ip.observaciones,
        
        -- Códigos
        ip.codigo_qr,
        ip.imagen_url,
        ip.codigo_barras,
        
        -- Reglas de negocio
        CASE WHEN ip.tipo IN ('ESTRUCTURAL', 'PRINCIPAL') THEN 1 ELSE 0 END as es_critico,
        1 as permite_reserva, -- Por defecto permitir reservas
        CASE WHEN ip.precio_unitario > 10000 THEN 1 ELSE 0 END as requiere_aprobacion,
        
        -- Control
        CASE 
            WHEN ip.activo = 1 AND ISNULL(ip.stock, 0) >= 0 THEN 'ACTIVO'
            WHEN ip.activo = 0 THEN 'INACTIVO'
            ELSE 'ACTIVO'
        END as estado,
        ISNULL(ip.activo, 1) as activo,
        ISNULL(ip.fecha_creacion, GETDATE()) as fecha_creacion,
        ISNULL(ip.fecha_modificacion, GETDATE()) as fecha_actualizacion,
        ISNULL(ip.usuario_creacion, 'MIGRACION') as usuario_creacion,
        ISNULL(ip.usuario_modificacion, 'MIGRACION') as usuario_modificacion,
        1 as version
        
    FROM inventario_perfiles ip
    WHERE ip.activo = 1 
        AND NOT EXISTS (
            SELECT 1 FROM productos p 
            WHERE p.codigo = ISNULL(ip.codigo, 'PERF-' + CAST(ip.id AS VARCHAR))
        );

    -- Obtener estadísticas de migración
    DECLARE @migrados INT;
    SELECT @migrados = @@ROWCOUNT;
    
    PRINT 'Registros migrados exitosamente: ' + CAST(@migrados AS VARCHAR);
    
    -- Verificar integridad de datos migrados
    DECLARE @errores INT = 0;
    
    -- Verificar códigos únicos
    IF EXISTS (SELECT codigo FROM productos WHERE categoria = 'PERFIL' GROUP BY codigo HAVING COUNT(*) > 1)
    BEGIN
        PRINT 'ERROR: Códigos duplicados detectados en productos PERFIL';
        SET @errores = @errores + 1;
    END
    
    -- Verificar stock negativo
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'PERFIL' AND stock_actual < 0)
    BEGIN
        PRINT 'ERROR: Stock negativo detectado en productos PERFIL';
        SET @errores = @errores + 1;
    END
    
    -- Verificar precios negativos
    IF EXISTS (SELECT * FROM productos WHERE categoria = 'PERFIL' AND precio_unitario < 0)
    BEGIN
        PRINT 'ERROR: Precios negativos detectados en productos PERFIL';
        SET @errores = @errores + 1;
    END
    
    IF @errores > 0
    BEGIN
        PRINT 'Se encontraron ' + CAST(@errores AS VARCHAR) + ' errores. Abortando migración.';
        ROLLBACK TRANSACTION MigrarInventario;
        RETURN;
    END
    
    -- Actualizar estadísticas
    UPDATE STATISTICS productos;
    
    -- Crear tabla de mapeo para referencia futura
    IF OBJECT_ID('mapeo_inventario_productos', 'U') IS NULL
    BEGIN
        CREATE TABLE mapeo_inventario_productos (
            id_original INT,
            tabla_original NVARCHAR(50),
            id_nuevo INT,
            codigo_nuevo NVARCHAR(50),
            fecha_migracion DATETIME DEFAULT GETDATE()
        );
        
        PRINT 'Tabla de mapeo creada: mapeo_inventario_productos';
    END
    
    -- Insertar mapeo
    INSERT INTO mapeo_inventario_productos (id_original, tabla_original, id_nuevo, codigo_nuevo)
    SELECT 
        ip.id,
        'inventario_perfiles',
        p.id,
        p.codigo
    FROM inventario_perfiles ip
    INNER JOIN productos p ON p.codigo = ISNULL(ip.codigo, 'PERF-' + CAST(ip.id AS VARCHAR))
    WHERE p.categoria = 'PERFIL'
        AND NOT EXISTS (
            SELECT 1 FROM mapeo_inventario_productos m 
            WHERE m.id_original = ip.id AND m.tabla_original = 'inventario_perfiles'
        );
    
    -- Confirmar transacción
    COMMIT TRANSACTION MigrarInventario;
    
    PRINT '';
    PRINT '=== MIGRACIÓN COMPLETADA EXITOSAMENTE ===';
    PRINT 'Total de perfiles migrados: ' + CAST(@migrados AS VARCHAR);
    
    -- Mostrar estadísticas finales
    SELECT 
        'PERFIL' as categoria,
        COUNT(*) as total_productos,
        SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
        SUM(CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END) as con_stock_bajo,
        SUM(CASE WHEN stock_actual = 0 THEN 1 ELSE 0 END) as sin_stock,
        CAST(SUM(stock_actual * precio_unitario) AS DECIMAL(18,2)) as valor_inventario,
        CAST(AVG(stock_actual) AS DECIMAL(10,2)) as promedio_stock
    FROM productos 
    WHERE categoria = 'PERFIL';
    
    PRINT '';
    PRINT 'Próximo paso: Ejecutar 03_migrar_herrajes_a_productos.sql';
    
END TRY
BEGIN CATCH
    -- Error en la migración
    ROLLBACK TRANSACTION MigrarInventario;
    
    PRINT '';
    PRINT '=== ERROR EN LA MIGRACIÓN ===';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT '';
    PRINT 'La migración ha sido revertida. Revise los errores y vuelva a intentar.';
    
END CATCH

GO