-- =====================================================
-- FASE 1.5: Crear Tabla Consolidada 'auditoria'
-- Reemplaza: auditoria_sistema, logs_usuarios, auditoria_log
-- =====================================================

USE users;
GO

PRINT '=== INICIANDO CREACIÓN: Tabla auditoria consolidada ===';
PRINT 'Fecha: ' + CONVERT(VARCHAR, GETDATE(), 120);
PRINT '';

-- Crear tabla auditoria consolidada
IF OBJECT_ID('auditoria', 'U') IS NULL
BEGIN
    CREATE TABLE auditoria (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        
        -- Event Classification
        nivel NVARCHAR(20) NOT NULL CHECK (nivel IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG')),
        categoria NVARCHAR(50) NOT NULL CHECK (categoria IN ('SISTEMA', 'USUARIO', 'NEGOCIO', 'SEGURIDAD', 'PERFORMANCE', 'INTEGRACION')),
        evento_tipo NVARCHAR(50) NOT NULL, -- LOGIN, LOGOUT, CREATE, UPDATE, DELETE, SELECT, EXECUTE, etc.
        
        -- Context
        modulo NVARCHAR(50) NOT NULL, -- inventario, obras, pedidos, usuarios, etc.
        accion NVARCHAR(100) NOT NULL, -- Descripción corta de la acción
        descripcion NTEXT, -- Descripción detallada del evento
        
        -- User & Session Info
        usuario_id INT,
        usuario_nombre NVARCHAR(100),
        session_id NVARCHAR(100),
        ip_address NVARCHAR(45), -- IPv4 or IPv6
        user_agent NVARCHAR(500),
        url_solicitada NVARCHAR(500), -- Para eventos web
        
        -- Data Changes (for audit trail)
        tabla_afectada NVARCHAR(100),
        registro_id NVARCHAR(50), -- ID del registro afectado
        valores_anteriores NTEXT, -- JSON con valores antes del cambio
        valores_nuevos NTEXT, -- JSON con valores después del cambio
        campos_modificados NVARCHAR(500), -- Lista de campos que cambiaron
        
        -- Operation Results
        resultado NVARCHAR(20) NOT NULL DEFAULT 'EXITOSO' CHECK (resultado IN ('EXITOSO', 'FALLIDO', 'WARNING', 'PARCIAL')),
        codigo_error INT,
        error_mensaje NTEXT,
        tiempo_ejecucion_ms INT,
        
        -- Additional Context
        parametros_entrada NTEXT, -- JSON con parámetros de entrada
        datos_adicionales NTEXT, -- JSON con información adicional del contexto
        referencia_externa NVARCHAR(255), -- Referencia a sistemas externos
        proceso_padre_id BIGINT, -- Para relacionar eventos de un mismo proceso
        
        -- Performance & Resource Usage
        memoria_utilizada_mb DECIMAL(10,2),
        cpu_tiempo_ms INT,
        registros_afectados INT,
        
        -- Geolocation (opcional)
        ubicacion_geografica NVARCHAR(100),
        zona_horaria NVARCHAR(50),
        
        -- Control Fields
        timestamp DATETIME DEFAULT GETDATE() NOT NULL,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_expiracion DATETIME, -- Para auto-limpieza de logs antiguos
        
        -- Indexing helpers
        fecha_date AS CAST(timestamp AS DATE) PERSISTED, -- Para índices por fecha
        hora_time AS CAST(timestamp AS TIME) PERSISTED, -- Para análisis por hora del día
        
        -- Security & Integrity
        hash_integridad NVARCHAR(64), -- SHA-256 para verificar integridad
        requiere_retencion BIT DEFAULT 0, -- Para cumplimiento legal
        
        -- Version Control
        version_esquema INT DEFAULT 1 -- Para evolución del esquema de auditoría
    );
    
    PRINT 'Tabla auditoria creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla auditoria ya existe - verificando estructura';
    
    -- Verificar y agregar columnas faltantes
    IF COL_LENGTH('auditoria', 'version_esquema') IS NULL
        ALTER TABLE auditoria ADD version_esquema INT DEFAULT 1;
    
    IF COL_LENGTH('auditoria', 'fecha_date') IS NULL
        ALTER TABLE auditoria ADD fecha_date AS CAST(timestamp AS DATE) PERSISTED;
        
    IF COL_LENGTH('auditoria', 'hora_time') IS NULL
        ALTER TABLE auditoria ADD hora_time AS CAST(timestamp AS TIME) PERSISTED;
END
GO

-- Crear índices para optimización de consultas de auditoría
PRINT 'Creando índices de optimización...';

-- Índice principal por fecha (más utilizado)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_fecha_nivel')
    CREATE INDEX IX_auditoria_fecha_nivel ON auditoria(fecha_date DESC, nivel, categoria);
GO

-- Índice por usuario y módulo
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_usuario_modulo')
    CREATE INDEX IX_auditoria_usuario_modulo ON auditoria(usuario_id, modulo, timestamp DESC);
GO

-- Índice por categoría y evento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_categoria_evento')
    CREATE INDEX IX_auditoria_categoria_evento ON auditoria(categoria, evento_tipo, timestamp DESC);
GO

-- Índice por resultado (para consultas de errores)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_resultado_timestamp')
    CREATE INDEX IX_auditoria_resultado_timestamp ON auditoria(resultado, timestamp DESC)
    WHERE resultado != 'EXITOSO';
GO

-- Índice por tabla afectada (para auditoría de cambios)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_tabla_registro')
    CREATE INDEX IX_auditoria_tabla_registro ON auditoria(tabla_afectada, registro_id, timestamp DESC)
    WHERE tabla_afectada IS NOT NULL;
GO

-- Índice por IP address (para análisis de seguridad)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_ip_usuario')
    CREATE INDEX IX_auditoria_ip_usuario ON auditoria(ip_address, usuario_id, timestamp DESC)
    WHERE ip_address IS NOT NULL;
GO

-- Crear vistas especializadas para diferentes tipos de consulta
PRINT 'Creando vistas especializadas...';

-- Vista para eventos de seguridad
IF OBJECT_ID('v_auditoria_seguridad', 'V') IS NOT NULL
    DROP VIEW v_auditoria_seguridad;
GO

CREATE VIEW v_auditoria_seguridad AS
SELECT 
    id, timestamp, nivel, evento_tipo, modulo, accion, descripcion,
    usuario_nombre, ip_address, resultado, error_mensaje,
    CASE 
        WHEN evento_tipo IN ('LOGIN_FAILED', 'UNAUTHORIZED_ACCESS', 'PRIVILEGE_ESCALATION') THEN 'ALTO'
        WHEN evento_tipo IN ('LOGIN', 'LOGOUT', 'PASSWORD_CHANGE') THEN 'MEDIO'
        ELSE 'BAJO'
    END as nivel_riesgo
FROM auditoria
WHERE categoria = 'SEGURIDAD' OR evento_tipo IN ('LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'UNAUTHORIZED_ACCESS');
GO

-- Vista para cambios en datos (Data Change Log)
IF OBJECT_ID('v_auditoria_cambios', 'V') IS NOT NULL
    DROP VIEW v_auditoria_cambios;
GO

CREATE VIEW v_auditoria_cambios AS
SELECT 
    id, timestamp, usuario_nombre, modulo, accion,
    tabla_afectada, registro_id, campos_modificados,
    valores_anteriores, valores_nuevos,
    resultado, registros_afectados
FROM auditoria
WHERE evento_tipo IN ('CREATE', 'UPDATE', 'DELETE') 
    AND tabla_afectada IS NOT NULL;
GO

-- Vista para errores del sistema
IF OBJECT_ID('v_auditoria_errores', 'V') IS NOT NULL
    DROP VIEW v_auditoria_errores;
GO

CREATE VIEW v_auditoria_errores AS
SELECT 
    id, timestamp, nivel, categoria, modulo, accion, descripcion,
    usuario_nombre, codigo_error, error_mensaje,
    tiempo_ejecucion_ms, registros_afectados,
    ip_address
FROM auditoria
WHERE resultado IN ('FALLIDO', 'ERROR') OR nivel IN ('ERROR', 'CRITICAL');
GO

-- Vista para estadísticas diarias
IF OBJECT_ID('v_auditoria_estadisticas_diarias', 'V') IS NOT NULL
    DROP VIEW v_auditoria_estadisticas_diarias;
GO

CREATE VIEW v_auditoria_estadisticas_diarias AS
SELECT 
    fecha_date,
    COUNT(*) as total_eventos,
    COUNT(DISTINCT usuario_id) as usuarios_activos,
    COUNT(DISTINCT ip_address) as ips_diferentes,
    SUM(CASE WHEN resultado = 'EXITOSO' THEN 1 ELSE 0 END) as eventos_exitosos,
    SUM(CASE WHEN resultado = 'FALLIDO' THEN 1 ELSE 0 END) as eventos_fallidos,
    SUM(CASE WHEN nivel = 'ERROR' THEN 1 ELSE 0 END) as errores,
    SUM(CASE WHEN categoria = 'SEGURIDAD' THEN 1 ELSE 0 END) as eventos_seguridad,
    AVG(tiempo_ejecucion_ms) as tiempo_promedio_ms
FROM auditoria
WHERE timestamp >= DATEADD(DAY, -30, GETDATE()) -- Últimos 30 días
GROUP BY fecha_date;
GO

-- Crear funciones útiles para auditoría
PRINT 'Creando funciones de utilidad...';

-- Función para generar hash de integridad
IF OBJECT_ID('fn_generar_hash_auditoria', 'FN') IS NOT NULL
    DROP FUNCTION fn_generar_hash_auditoria;
GO

CREATE FUNCTION fn_generar_hash_auditoria(
    @usuario_id INT,
    @evento_tipo NVARCHAR(50),
    @tabla_afectada NVARCHAR(100),
    @registro_id NVARCHAR(50),
    @timestamp DATETIME
)
RETURNS NVARCHAR(64)
AS
BEGIN
    DECLARE @cadena NVARCHAR(500);
    SET @cadena = CONCAT(
        ISNULL(CAST(@usuario_id AS NVARCHAR), ''),
        ISNULL(@evento_tipo, ''),
        ISNULL(@tabla_afectada, ''),
        ISNULL(@registro_id, ''),
        FORMAT(@timestamp, 'yyyy-MM-dd HH:mm:ss.fff')
    );
    
    RETURN CONVERT(NVARCHAR(64), HASHBYTES('SHA2_256', @cadena), 2);
END
GO

-- Crear procedimiento para insertar eventos de auditoría
IF OBJECT_ID('sp_insertar_auditoria', 'P') IS NOT NULL
    DROP PROCEDURE sp_insertar_auditoria;
GO

CREATE PROCEDURE sp_insertar_auditoria
    @nivel NVARCHAR(20) = 'INFO',
    @categoria NVARCHAR(50) = 'SISTEMA',
    @evento_tipo NVARCHAR(50),
    @modulo NVARCHAR(50),
    @accion NVARCHAR(100),
    @descripcion NTEXT = NULL,
    @usuario_id INT = NULL,
    @usuario_nombre NVARCHAR(100) = NULL,
    @ip_address NVARCHAR(45) = NULL,
    @tabla_afectada NVARCHAR(100) = NULL,
    @registro_id NVARCHAR(50) = NULL,
    @valores_anteriores NTEXT = NULL,
    @valores_nuevos NTEXT = NULL,
    @resultado NVARCHAR(20) = 'EXITOSO',
    @error_mensaje NTEXT = NULL,
    @tiempo_ejecucion_ms INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @timestamp DATETIME = GETDATE();
    DECLARE @hash_integridad NVARCHAR(64);
    
    -- Generar hash de integridad
    SET @hash_integridad = dbo.fn_generar_hash_auditoria(@usuario_id, @evento_tipo, @tabla_afectada, @registro_id, @timestamp);
    
    INSERT INTO auditoria (
        nivel, categoria, evento_tipo, modulo, accion, descripcion,
        usuario_id, usuario_nombre, ip_address,
        tabla_afectada, registro_id, valores_anteriores, valores_nuevos,
        resultado, error_mensaje, tiempo_ejecucion_ms, timestamp, hash_integridad
    )
    VALUES (
        @nivel, @categoria, @evento_tipo, @modulo, @accion, @descripcion,
        @usuario_id, @usuario_nombre, @ip_address,
        @tabla_afectada, @registro_id, @valores_anteriores, @valores_nuevos,
        @resultado, @error_mensaje, @tiempo_ejecucion_ms, @timestamp, @hash_integridad
    );
    
    RETURN @@IDENTITY;
END
GO

-- Crear trigger para auto-limpieza de registros antiguos (opcional)
IF OBJECT_ID('TR_auditoria_auto_cleanup', 'TR') IS NOT NULL
    DROP TRIGGER TR_auditoria_auto_cleanup;
GO

-- Job de limpieza se ejecutará por separado para no impactar performance

-- Crear procedimiento para limpieza de registros antiguos
IF OBJECT_ID('sp_limpiar_auditoria_antigua', 'P') IS NOT NULL
    DROP PROCEDURE sp_limpiar_auditoria_antigua;
GO

CREATE PROCEDURE sp_limpiar_auditoria_antigua
    @dias_retencion INT = 365,
    @batch_size INT = 10000
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @fecha_limite DATETIME = DATEADD(DAY, -@dias_retencion, GETDATE());
    DECLARE @registros_eliminados INT = 0;
    DECLARE @total_eliminados INT = 0;
    
    PRINT 'Iniciando limpieza de registros de auditoría anteriores a: ' + CONVERT(VARCHAR, @fecha_limite, 120);
    
    WHILE 1 = 1
    BEGIN
        DELETE TOP (@batch_size) FROM auditoria 
        WHERE timestamp < @fecha_limite 
            AND requiere_retencion = 0
            AND nivel NOT IN ('CRITICAL'); -- Mantener eventos críticos por más tiempo
        
        SET @registros_eliminados = @@ROWCOUNT;
        SET @total_eliminados = @total_eliminados + @registros_eliminados;
        
        IF @registros_eliminados = 0 BREAK;
        
        PRINT 'Eliminados: ' + CAST(@registros_eliminados AS VARCHAR) + ' registros (Total: ' + CAST(@total_eliminados AS VARCHAR) + ')';
        
        -- Pausa para evitar bloqueos
        WAITFOR DELAY '00:00:01';
    END
    
    PRINT 'Limpieza completada. Total eliminados: ' + CAST(@total_eliminados AS VARCHAR);
END
GO

PRINT '';
PRINT '=== TABLA AUDITORIA CONSOLIDADA CREADA EXITOSAMENTE ===';
PRINT 'Índices creados: 6';
PRINT 'Vistas creadas: 4';
PRINT 'Funciones creadas: 1';
PRINT 'Procedimientos creados: 2';
PRINT '';
PRINT 'Características principales:';
PRINT '- Sistema de auditoría unificado';
PRINT '- Categorización por nivel y tipo de evento';
PRINT '- Seguimiento de cambios en datos (audit trail)';
PRINT '- Análisis de seguridad y performance';
PRINT '- Auto-limpieza de registros antiguos';
PRINT '- Hash de integridad para verificación';
PRINT '';
PRINT 'Próximo paso: Ejecutar 06_migrar_datos_auditoria.sql';
GO