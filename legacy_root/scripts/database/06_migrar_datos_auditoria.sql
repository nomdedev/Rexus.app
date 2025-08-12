-- =====================================================
-- FASE 1.6: Migrar datos existentes a tabla auditoria consolidada
-- Migra: auditoria_sistema, logs_usuarios, auditoria_log
-- =====================================================

USE users;
GO

PRINT '=== INICIANDO MIGRACIÓN: Datos de auditoría → auditoria consolidada ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Verificar que la tabla auditoria consolidada existe
IF OBJECT_ID('auditoria', 'U') IS NULL
BEGIN
    PRINT 'ERROR: La tabla auditoria no existe. Ejecute primero 05_crear_tabla_auditoria.sql';
    RETURN;
END

-- Inicializar contadores
DECLARE @total_migrados INT = 0;
DECLARE @errores INT = 0;

PRINT 'Iniciando migración de datos existentes...';

-- Iniciar transacción
BEGIN TRANSACTION MigrarAuditoria;

BEGIN TRY
    -- ==============================================
    -- MIGRAR auditoria_sistema
    -- ==============================================
    IF OBJECT_ID('auditoria_sistema', 'U') IS NOT NULL
    BEGIN
        PRINT 'Migrando datos de auditoria_sistema...';
        
        INSERT INTO auditoria (
            nivel, categoria, evento_tipo, modulo, accion, descripcion,
            usuario_id, usuario_nombre, ip_address,
            resultado, error_mensaje, timestamp
        )
        SELECT 
            CASE 
                WHEN UPPER(aus.nivel) IN ('ERROR', 'CRITICAL', 'FATAL') THEN 'ERROR'
                WHEN UPPER(aus.nivel) = 'WARNING' THEN 'WARNING'
                WHEN UPPER(aus.nivel) = 'DEBUG' THEN 'DEBUG'
                ELSE 'INFO'
            END as nivel,
            
            CASE 
                WHEN aus.evento LIKE '%LOGIN%' OR aus.evento LIKE '%LOGOUT%' OR aus.evento LIKE '%AUTH%' THEN 'SEGURIDAD'
                WHEN aus.evento LIKE '%SISTEMA%' OR aus.evento LIKE '%SERVER%' OR aus.evento LIKE '%DATABASE%' THEN 'SISTEMA'
                WHEN aus.evento LIKE '%USER%' OR aus.evento LIKE '%USUARIO%' THEN 'USUARIO'
                ELSE 'SISTEMA'
            END as categoria,
            
            CASE 
                WHEN aus.evento LIKE '%LOGIN%' THEN 'LOGIN'
                WHEN aus.evento LIKE '%LOGOUT%' THEN 'LOGOUT'
                WHEN aus.evento LIKE '%CREATE%' THEN 'CREATE'
                WHEN aus.evento LIKE '%UPDATE%' THEN 'UPDATE'
                WHEN aus.evento LIKE '%DELETE%' THEN 'DELETE'
                WHEN aus.evento LIKE '%ERROR%' THEN 'ERROR'
                ELSE 'SYSTEM_EVENT'
            END as evento_tipo,
            
            ISNULL(aus.modulo, 'SISTEMA') as modulo,
            ISNULL(aus.accion, aus.evento) as accion,
            aus.descripcion,
            aus.usuario_id,
            aus.usuario_nombre,
            aus.ip_address,
            
            CASE 
                WHEN aus.resultado = 'EXITOSO' OR aus.nivel = 'INFO' THEN 'EXITOSO'
                WHEN aus.resultado = 'ERROR' OR aus.nivel IN ('ERROR', 'CRITICAL') THEN 'FALLIDO'
                ELSE 'EXITOSO'
            END as resultado,
            
            aus.error_detalle as error_mensaje,
            ISNULL(aus.fecha_evento, aus.fecha_creacion) as timestamp
            
        FROM auditoria_sistema aus
        WHERE NOT EXISTS (
            SELECT 1 FROM auditoria a 
            WHERE a.timestamp = ISNULL(aus.fecha_evento, aus.fecha_creacion)
                AND a.usuario_id = aus.usuario_id
                AND a.accion = ISNULL(aus.accion, aus.evento)
        );
        
        DECLARE @migrados_sistema INT = @@ROWCOUNT;
        SET @total_migrados = @total_migrados + @migrados_sistema;
        PRINT 'Migrados de auditoria_sistema: ' + CAST(@migrados_sistema AS VARCHAR);
    END
    ELSE
    BEGIN
        PRINT 'Tabla auditoria_sistema no existe - saltando';
    END

    -- ==============================================
    -- MIGRAR logs_usuarios
    -- ==============================================
    IF OBJECT_ID('logs_usuarios', 'U') IS NOT NULL
    BEGIN
        PRINT 'Migrando datos de logs_usuarios...';
        
        INSERT INTO auditoria (
            nivel, categoria, evento_tipo, modulo, accion, descripcion,
            usuario_id, usuario_nombre, ip_address,
            resultado, timestamp
        )
        SELECT 
            'INFO' as nivel,
            'USUARIO' as categoria,
            
            CASE 
                WHEN lu.accion LIKE '%LOGIN%' THEN 'LOGIN'
                WHEN lu.accion LIKE '%LOGOUT%' THEN 'LOGOUT'
                WHEN lu.accion LIKE '%CREATE%' THEN 'CREATE'
                WHEN lu.accion LIKE '%UPDATE%' OR lu.accion LIKE '%EDIT%' THEN 'UPDATE'
                WHEN lu.accion LIKE '%DELETE%' THEN 'DELETE'
                WHEN lu.accion LIKE '%VIEW%' OR lu.accion LIKE '%READ%' THEN 'SELECT'
                ELSE 'USER_ACTION'
            END as evento_tipo,
            
            ISNULL(lu.modulo, 'USUARIOS') as modulo,
            lu.accion,
            COALESCE(lu.descripcion, lu.detalle, 'Acción de usuario') as descripcion,
            lu.usuario_id,
            lu.usuario_nombre,
            lu.ip_address,
            'EXITOSO' as resultado, -- Los logs de usuario suelen ser acciones exitosas
            ISNULL(lu.fecha_hora, lu.fecha) as timestamp
            
        FROM logs_usuarios lu
        WHERE NOT EXISTS (
            SELECT 1 FROM auditoria a 
            WHERE a.timestamp = ISNULL(lu.fecha_hora, lu.fecha)
                AND a.usuario_id = lu.usuario_id
                AND a.accion = lu.accion
        );
        
        DECLARE @migrados_usuarios INT = @@ROWCOUNT;
        SET @total_migrados = @total_migrados + @migrados_usuarios;
        PRINT 'Migrados de logs_usuarios: ' + CAST(@migrados_usuarios AS VARCHAR);
    END
    ELSE
    BEGIN
        PRINT 'Tabla logs_usuarios no existe - saltando';
    END

    -- ==============================================
    -- MIGRAR auditoria_log (si existe)
    -- ==============================================
    IF OBJECT_ID('auditoria_log', 'U') IS NOT NULL
    BEGIN
        PRINT 'Migrando datos de auditoria_log...';
        
        INSERT INTO auditoria (
            nivel, categoria, evento_tipo, modulo, accion, descripcion,
            usuario_id, usuario_nombre, 
            tabla_afectada, registro_id, valores_anteriores, valores_nuevos,
            resultado, timestamp
        )
        SELECT 
            CASE 
                WHEN al.tipo_evento = 'ERROR' THEN 'ERROR'
                WHEN al.tipo_evento = 'WARNING' THEN 'WARNING'
                ELSE 'INFO'
            END as nivel,
            
            'NEGOCIO' as categoria,
            
            CASE 
                WHEN al.operacion = 'INSERT' THEN 'CREATE'
                WHEN al.operacion = 'UPDATE' THEN 'UPDATE'
                WHEN al.operacion = 'DELETE' THEN 'DELETE'
                WHEN al.operacion = 'SELECT' THEN 'SELECT'
                ELSE 'BUSINESS_EVENT'
            END as evento_tipo,
            
            ISNULL(al.modulo, 'GENERAL') as modulo,
            ISNULL(al.accion, al.operacion) as accion,
            al.descripcion,
            al.usuario_id,
            al.usuario_nombre,
            al.tabla_afectada,
            CAST(al.registro_id AS NVARCHAR(50)) as registro_id,
            al.valores_anteriores,
            al.valores_nuevos,
            
            CASE 
                WHEN al.exitoso = 1 THEN 'EXITOSO'
                ELSE 'FALLIDO'
            END as resultado,
            
            al.fecha_evento as timestamp
            
        FROM auditoria_log al
        WHERE NOT EXISTS (
            SELECT 1 FROM auditoria a 
            WHERE a.timestamp = al.fecha_evento
                AND a.usuario_id = al.usuario_id
                AND a.tabla_afectada = al.tabla_afectada
                AND a.registro_id = CAST(al.registro_id AS NVARCHAR(50))
        );
        
        DECLARE @migrados_log INT = @@ROWCOUNT;
        SET @total_migrados = @total_migrados + @migrados_log;
        PRINT 'Migrados de auditoria_log: ' + CAST(@migrados_log AS VARCHAR);
    END
    ELSE
    BEGIN
        PRINT 'Tabla auditoria_log no existe - saltando';
    END

    -- ==============================================
    -- VERIFICACIÓN DE INTEGRIDAD
    -- ==============================================
    PRINT '';
    PRINT 'Verificando integridad de datos migrados...';
    
    -- Verificar que no hay valores nulos en campos requeridos
    IF EXISTS (SELECT * FROM auditoria WHERE nivel IS NULL OR categoria IS NULL OR evento_tipo IS NULL OR modulo IS NULL)
    BEGIN
        PRINT 'ERROR: Valores nulos encontrados en campos requeridos';
        SET @errores = @errores + 1;
    END
    
    -- Verificar valores válidos en campos con CHECK constraints
    IF EXISTS (SELECT * FROM auditoria WHERE nivel NOT IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'))
    BEGIN
        PRINT 'ERROR: Valores inválidos en campo nivel';
        SET @errores = @errores + 1;
    END
    
    IF EXISTS (SELECT * FROM auditoria WHERE categoria NOT IN ('SISTEMA', 'USUARIO', 'NEGOCIO', 'SEGURIDAD', 'PERFORMANCE', 'INTEGRACION'))
    BEGIN
        PRINT 'ERROR: Valores inválidos en campo categoria';
        SET @errores = @errores + 1;
    END
    
    IF EXISTS (SELECT * FROM auditoria WHERE resultado NOT IN ('EXITOSO', 'FALLIDO', 'WARNING', 'PARCIAL'))
    BEGIN
        PRINT 'ERROR: Valores inválidos en campo resultado';
        SET @errores = @errores + 1;
    END
    
    IF @errores > 0
    BEGIN
        PRINT 'Se encontraron ' + CAST(@errores AS VARCHAR) + ' errores. Abortando migración.';
        ROLLBACK TRANSACTION MigrarAuditoria;
        RETURN;
    END
    
    -- Actualizar estadísticas
    UPDATE STATISTICS auditoria;
    
    -- Confirmar transacción
    COMMIT TRANSACTION MigrarAuditoria;
    
    PRINT '';
    PRINT '=== MIGRACIÓN DE AUDITORÍA COMPLETADA EXITOSAMENTE ===';
    PRINT 'Total de registros migrados: ' + CAST(@total_migrados AS VARCHAR);
    
    -- Mostrar estadísticas de la auditoría consolidada
    SELECT 
        categoria,
        COUNT(*) as total_registros,
        COUNT(DISTINCT usuario_id) as usuarios_diferentes,
        MIN(timestamp) as evento_mas_antiguo,
        MAX(timestamp) as evento_mas_reciente,
        SUM(CASE WHEN resultado = 'EXITOSO' THEN 1 ELSE 0 END) as eventos_exitosos,
        SUM(CASE WHEN resultado = 'FALLIDO' THEN 1 ELSE 0 END) as eventos_fallidos,
        SUM(CASE WHEN nivel = 'ERROR' THEN 1 ELSE 0 END) as errores
    FROM auditoria
    GROUP BY categoria
    ORDER BY total_registros DESC;
    
    PRINT '';
    PRINT 'Resumen por tipo de evento:';
    SELECT TOP 10
        evento_tipo,
        COUNT(*) as total_eventos,
        COUNT(DISTINCT usuario_id) as usuarios_diferentes
    FROM auditoria
    GROUP BY evento_tipo
    ORDER BY total_eventos DESC;
    
    PRINT '';
    PRINT '=== FASE 1 COMPLETADA TOTALMENTE ===';
    PRINT 'Próximo paso: Ejecutar 07_crear_sistema_pedidos.sql (FASE 2)';
    
END TRY
BEGIN CATCH
    -- Error en la migración
    ROLLBACK TRANSACTION MigrarAuditoria;
    
    PRINT '';
    PRINT '=== ERROR EN LA MIGRACIÓN ===';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR);
    PRINT 'Error Message: ' + ERROR_MESSAGE();
    PRINT 'Error Line: ' + CAST(ERROR_LINE() AS VARCHAR);
    PRINT '';
    PRINT 'La migración ha sido revertida. Revise los errores y vuelva a intentar.';
    
END CATCH

GO