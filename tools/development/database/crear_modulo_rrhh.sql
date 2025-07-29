-- ============================================================================
-- MÓDULO DE RECURSOS HUMANOS Y CONTABILIDAD - ESTRUCTURA DE BASE DE DATOS
-- ============================================================================
-- Creación de tablas para gestión integral de empleados
-- Fecha: 26/06/2025
-- Versión: 1.0
-- ============================================================================

-- Crear esquema si no existe
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'rrhh')
BEGIN
    EXEC('CREATE SCHEMA rrhh')
END
GO

-- ============================================================================
-- TABLA PRINCIPAL: EMPLEADOS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='empleados' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.empleados (
        id INT IDENTITY(1,1) PRIMARY KEY,

        -- Datos personales básicos
        nombre_completo NVARCHAR(200) NOT NULL,
        dni_cuit NVARCHAR(20) UNIQUE NOT NULL,
        fecha_nacimiento DATE,
        direccion_completa NVARCHAR(500),
        telefono_principal NVARCHAR(50),
        telefono_secundario NVARCHAR(50),
        email_personal NVARCHAR(200),
        email_corporativo NVARCHAR(200),
        estado_civil NVARCHAR(50),

        -- Contacto de emergencia
        contacto_emergencia_nombre NVARCHAR(200),
        contacto_emergencia_telefono NVARCHAR(50),
        contacto_emergencia_relacion NVARCHAR(100),

        -- Datos laborales básicos
        legajo_numero NVARCHAR(50) UNIQUE,
        fecha_ingreso DATE NOT NULL,
        estado_actual NVARCHAR(50) DEFAULT 'activo' CHECK (estado_actual IN ('activo', 'periodo_prueba', 'suspendido', 'inactivo', 'despedido')),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        fecha_modificacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),
        usuario_modificacion NVARCHAR(100),
        activo BIT DEFAULT 1,

        -- Índices
        INDEX IX_empleados_dni_cuit (dni_cuit),
        INDEX IX_empleados_legajo (legajo_numero),
        INDEX IX_empleados_estado (estado_actual),
        INDEX IX_empleados_activo (activo)
    )
    PRINT '✅ Tabla rrhh.empleados creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.empleados ya existe'
GO

-- ============================================================================
-- TABLA: CATEGORÍAS LABORALES
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='categorias_laborales' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.categorias_laborales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nombre_categoria NVARCHAR(200) NOT NULL,
        codigo_categoria NVARCHAR(50) UNIQUE,
        departamento NVARCHAR(100),
        nivel_jerarquico NVARCHAR(100),
        descripcion NVARCHAR(1000),
        salario_base_minimo DECIMAL(15,2),
        salario_base_maximo DECIMAL(15,2),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        fecha_modificacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),
        activa BIT DEFAULT 1,

        INDEX IX_categorias_codigo (codigo_categoria),
        INDEX IX_categorias_departamento (departamento),
        INDEX IX_categorias_activa (activa)
    )
    PRINT '✅ Tabla rrhh.categorias_laborales creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.categorias_laborales ya existe'
GO

-- ============================================================================
-- TABLA: CONTRATOS LABORALES
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='contratos_laborales' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.contratos_laborales (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,
        categoria_id INT NOT NULL,

        -- Información del contrato
        tipo_contrato NVARCHAR(100) NOT NULL CHECK (tipo_contrato IN ('indefinido', 'plazo_fijo', 'periodo_prueba', 'temporal', 'pasantia')),
        fecha_inicio DATE NOT NULL,
        fecha_finalizacion DATE,
        modalidad_trabajo NVARCHAR(50) DEFAULT 'presencial' CHECK (modalidad_trabajo IN ('presencial', 'remoto', 'hibrido')),

        -- Condiciones laborales
        horas_semanales INT DEFAULT 40,
        dias_laborales INT DEFAULT 5,
        turno NVARCHAR(50),

        -- Observaciones
        observaciones NVARCHAR(1000),
        archivo_contrato NVARCHAR(500), -- Ruta del archivo digitalizado

        -- Estado del contrato
        estado_contrato NVARCHAR(50) DEFAULT 'activo' CHECK (estado_contrato IN ('activo', 'finalizado', 'rescindido', 'suspendido')),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),
        FOREIGN KEY (categoria_id) REFERENCES rrhh.categorias_laborales(id),

        INDEX IX_contratos_empleado (empleado_id),
        INDEX IX_contratos_categoria (categoria_id),
        INDEX IX_contratos_estado (estado_contrato),
        INDEX IX_contratos_tipo (tipo_contrato)
    )
    PRINT '✅ Tabla rrhh.contratos_laborales creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.contratos_laborales ya existe'
GO

-- ============================================================================
-- TABLA: HISTORIAL DE CATEGORÍAS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historial_categorias' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.historial_categorias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,
        categoria_anterior_id INT,
        categoria_nueva_id INT NOT NULL,
        contrato_id INT,

        -- Información del cambio
        fecha_cambio DATE NOT NULL,
        fecha_efectiva DATE NOT NULL,
        motivo NVARCHAR(500) NOT NULL,
        tipo_cambio NVARCHAR(100) CHECK (tipo_cambio IN ('promocion', 'reasignacion', 'degradacion', 'transferencia')),

        -- Autorización
        usuario_autoriza NVARCHAR(100) NOT NULL,
        documento_autorizacion NVARCHAR(500),
        observaciones NVARCHAR(1000),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),
        FOREIGN KEY (categoria_anterior_id) REFERENCES rrhh.categorias_laborales(id),
        FOREIGN KEY (categoria_nueva_id) REFERENCES rrhh.categorias_laborales(id),
        FOREIGN KEY (contrato_id) REFERENCES rrhh.contratos_laborales(id),

        INDEX IX_historial_cat_empleado (empleado_id),
        INDEX IX_historial_cat_fecha (fecha_cambio),
        INDEX IX_historial_cat_tipo (tipo_cambio)
    )
    PRINT '✅ Tabla rrhh.historial_categorias creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.historial_categorias ya existe'
GO

-- ============================================================================
-- TABLA: HISTORIAL SALARIAL
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historial_salarial' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.historial_salarial (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,

        -- Información salarial
        salario_anterior DECIMAL(15,2),
        salario_nuevo DECIMAL(15,2) NOT NULL,
        fecha_cambio DATE NOT NULL,
        fecha_efectiva DATE NOT NULL,

        -- Análisis del cambio
        diferencia_absoluta AS (salario_nuevo - salario_anterior),
        porcentaje_aumento AS (
            CASE
                WHEN salario_anterior > 0 THEN
                    ROUND(((salario_nuevo - salario_anterior) / salario_anterior) * 100, 2)
                ELSE 0
            END
        ),

        -- Motivo y autorización
        motivo_ajuste NVARCHAR(500) NOT NULL,
        tipo_ajuste NVARCHAR(100) CHECK (tipo_ajuste IN ('aumento_general', 'merito', 'promocion', 'inflacion', 'convenio', 'correccion')),
        usuario_autoriza NVARCHAR(100) NOT NULL,
        documento_autorizacion NVARCHAR(500),

        -- Observaciones
        observaciones NVARCHAR(1000),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),

        INDEX IX_historial_sal_empleado (empleado_id),
        INDEX IX_historial_sal_fecha (fecha_cambio),
        INDEX IX_historial_sal_tipo (tipo_ajuste)
    )
    PRINT '✅ Tabla rrhh.historial_salarial creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.historial_salarial ya existe'
GO

-- ============================================================================
-- TABLA: PREMIOS Y RECONOCIMIENTOS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='premios_reconocimientos' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.premios_reconocimientos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,

        -- Información del premio
        tipo_premio NVARCHAR(100) NOT NULL CHECK (tipo_premio IN (
            'rendimiento', 'antiguedad', 'objetivos', 'reconocimiento_especial',
            'productividad', 'innovacion', 'liderazgo', 'trabajo_equipo'
        )),
        nombre_premio NVARCHAR(200) NOT NULL,
        descripcion NVARCHAR(1000),

        -- Valor del premio
        monto_valor DECIMAL(15,2),
        tipo_valor NVARCHAR(50) CHECK (tipo_valor IN ('monetario', 'puntos', 'dias_libres', 'capacitacion', 'otro')),

        -- Fechas y período
        fecha_otorgamiento DATE NOT NULL,
        periodo_evaluado_inicio DATE,
        periodo_evaluado_fin DATE,

        -- Autorización y documentación
        usuario_autoriza NVARCHAR(100) NOT NULL,
        documento_respaldo NVARCHAR(500),
        publico BIT DEFAULT 0, -- Si el premio es público o privado

        -- Observaciones
        observaciones NVARCHAR(1000),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),

        INDEX IX_premios_empleado (empleado_id),
        INDEX IX_premios_tipo (tipo_premio),
        INDEX IX_premios_fecha (fecha_otorgamiento)
    )
    PRINT '✅ Tabla rrhh.premios_reconocimientos creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.premios_reconocimientos ya existe'
GO

-- ============================================================================
-- TABLA: SANCIONES DISCIPLINARIAS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='sanciones_disciplinarias' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.sanciones_disciplinarias (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,

        -- Información de la sanción
        tipo_sancion NVARCHAR(100) NOT NULL CHECK (tipo_sancion IN (
            'llamado_atencion_verbal', 'apercibimiento_escrito', 'suspension_con_goce',
            'suspension_sin_goce', 'descuento_salarial', 'capacitacion_obligatoria'
        )),
        gravedad NVARCHAR(50) CHECK (gravedad IN ('leve', 'moderada', 'grave', 'muy_grave')),

        -- Motivo y descripción
        motivo_detallado NVARCHAR(1000) NOT NULL,
        incidente_fecha DATE,
        incidente_descripcion NVARCHAR(2000),

        -- Detalles de la sanción
        fecha_sancion DATE NOT NULL,
        fecha_inicio_cumplimiento DATE,
        duracion_dias INT,
        monto_descuento DECIMAL(15,2),

        -- Estado y seguimiento
        estado_sancion NVARCHAR(50) DEFAULT 'activa' CHECK (estado_sancion IN ('activa', 'cumplida', 'anulada', 'suspendida')),
        fecha_cumplimiento DATE,
        motivo_anulacion NVARCHAR(500),

        -- Autorización y documentación
        usuario_aplica NVARCHAR(100) NOT NULL,
        usuario_autoriza NVARCHAR(100),
        documento_sancion NVARCHAR(500),
        testigos NVARCHAR(500),

        -- Observaciones y seguimiento
        observaciones NVARCHAR(1000),
        acciones_correctivas NVARCHAR(1000),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        fecha_modificacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),
        usuario_modificacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),

        INDEX IX_sanciones_empleado (empleado_id),
        INDEX IX_sanciones_tipo (tipo_sancion),
        INDEX IX_sanciones_estado (estado_sancion),
        INDEX IX_sanciones_fecha (fecha_sancion),
        INDEX IX_sanciones_gravedad (gravedad)
    )
    PRINT '✅ Tabla rrhh.sanciones_disciplinarias creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.sanciones_disciplinarias ya existe'
GO

-- ============================================================================
-- TABLA: NOTIFICACIONES A EMPLEADOS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='notificaciones_empleados' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.notificaciones_empleados (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,

        -- Información de la notificación
        titulo NVARCHAR(200) NOT NULL,
        descripcion NVARCHAR(2000) NOT NULL,
        tipo_notificacion NVARCHAR(100) CHECK (tipo_notificacion IN (
            'recordatorio_administrativo', 'vencimiento_documentacion', 'evaluacion_pendiente',
            'capacitacion_obligatoria', 'renovacion_contrato', 'cambio_politica',
            'informacion_general', 'felicitacion', 'advertencia'
        )),

        -- Fechas importantes
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        fecha_vencimiento DATE,
        fecha_lectura DATETIME2,
        fecha_completada DATETIME2,

        -- Prioridad y estado
        prioridad NVARCHAR(50) DEFAULT 'media' CHECK (prioridad IN ('baja', 'media', 'alta', 'critica')),
        estado NVARCHAR(50) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'leida', 'completada', 'vencida')),
        requiere_accion BIT DEFAULT 0,
        acciones_requeridas NVARCHAR(1000),

        -- Seguimiento
        recordatorio_automatico BIT DEFAULT 0,
        dias_recordatorio INT,
        cantidad_recordatorios_enviados INT DEFAULT 0,

        -- Autorización y documentación
        usuario_crea NVARCHAR(100) NOT NULL,
        documento_adjunto NVARCHAR(500),

        -- Observaciones
        observaciones NVARCHAR(1000),
        respuesta_empleado NVARCHAR(2000),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),

        INDEX IX_notificaciones_empleado (empleado_id),
        INDEX IX_notificaciones_tipo (tipo_notificacion),
        INDEX IX_notificaciones_estado (estado),
        INDEX IX_notificaciones_prioridad (prioridad),
        INDEX IX_notificaciones_vencimiento (fecha_vencimiento)
    )
    PRINT '✅ Tabla rrhh.notificaciones_empleados creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.notificaciones_empleados ya existe'
GO

-- ============================================================================
-- TABLA: EVALUACIONES DE DESEMPEÑO
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='evaluaciones_desempeno' AND xtype='U')
BEGIN
    CREATE TABLE rrhh.evaluaciones_desempeno (
        id INT IDENTITY(1,1) PRIMARY KEY,
        empleado_id INT NOT NULL,

        -- Información de la evaluación
        periodo_evaluacion NVARCHAR(100) NOT NULL, -- "2025-Q1", "2025-Anual", etc.
        fecha_evaluacion DATE NOT NULL,
        tipo_evaluacion NVARCHAR(100) CHECK (tipo_evaluacion IN (
            'trimestral', 'semestral', 'anual', 'periodo_prueba', 'especial'
        )),

        -- Evaluador
        evaluador_usuario NVARCHAR(100) NOT NULL,
        evaluador_nombre NVARCHAR(200),

        -- Puntuaciones (escala 1-10)
        puntaje_rendimiento DECIMAL(3,1),
        puntaje_calidad DECIMAL(3,1),
        puntaje_puntualidad DECIMAL(3,1),
        puntaje_trabajo_equipo DECIMAL(3,1),
        puntaje_iniciativa DECIMAL(3,1),
        puntaje_liderazgo DECIMAL(3,1),
        puntaje_comunicacion DECIMAL(3,1),
        puntaje_general AS (
            (ISNULL(puntaje_rendimiento, 0) + ISNULL(puntaje_calidad, 0) +
             ISNULL(puntaje_puntualidad, 0) + ISNULL(puntaje_trabajo_equipo, 0) +
             ISNULL(puntaje_iniciativa, 0) + ISNULL(puntaje_liderazgo, 0) +
             ISNULL(puntaje_comunicacion, 0)) / 7.0
        ),

        -- Comentarios y observaciones
        fortalezas NVARCHAR(2000),
        areas_mejora NVARCHAR(2000),
        objetivos_proximos NVARCHAR(2000),
        comentarios_evaluador NVARCHAR(2000),
        comentarios_empleado NVARCHAR(2000),

        -- Acciones derivadas
        recomienda_aumento BIT DEFAULT 0,
        recomienda_promocion BIT DEFAULT 0,
        requiere_plan_mejora BIT DEFAULT 0,
        requiere_capacitacion BIT DEFAULT 0,
        capacitaciones_sugeridas NVARCHAR(1000),

        -- Estado
        estado_evaluacion NVARCHAR(50) DEFAULT 'borrador' CHECK (estado_evaluacion IN (
            'borrador', 'pendiente_revision', 'finalizada', 'aprobada'
        )),
        fecha_aprobacion DATE,
        usuario_aprueba NVARCHAR(100),

        -- Campos de auditoría
        fecha_creacion DATETIME2 DEFAULT GETDATE(),
        fecha_modificacion DATETIME2 DEFAULT GETDATE(),
        usuario_creacion NVARCHAR(100),

        -- Claves foráneas
        FOREIGN KEY (empleado_id) REFERENCES rrhh.empleados(id),

        INDEX IX_evaluaciones_empleado (empleado_id),
        INDEX IX_evaluaciones_periodo (periodo_evaluacion),
        INDEX IX_evaluaciones_tipo (tipo_evaluacion),
        INDEX IX_evaluaciones_estado (estado_evaluacion),
        INDEX IX_evaluaciones_fecha (fecha_evaluacion)
    )
    PRINT '✅ Tabla rrhh.evaluaciones_desempeno creada exitosamente'
END
ELSE
    PRINT '⚠️ Tabla rrhh.evaluaciones_desempeno ya existe'
GO

-- ============================================================================
-- TRIGGERS PARA AUDITORÍA AUTOMÁTICA
-- ============================================================================

-- Trigger para actualizar fecha_modificacion en empleados
IF NOT EXISTS (SELECT * FROM sys.triggers WHERE name = 'tr_empleados_update')
BEGIN
    EXEC('
    CREATE TRIGGER rrhh.tr_empleados_update
    ON rrhh.empleados
    AFTER UPDATE
    AS
    BEGIN
        UPDATE rrhh.empleados
        SET fecha_modificacion = GETDATE(),
            usuario_modificacion = SYSTEM_USER
        WHERE id IN (SELECT id FROM inserted)
    END
    ')
    PRINT '✅ Trigger tr_empleados_update creado exitosamente'
END
GO

-- ============================================================================
-- DATOS INICIALES - CATEGORÍAS LABORALES BÁSICAS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM rrhh.categorias_laborales WHERE codigo_categoria = 'ADM-001')
BEGIN
    INSERT INTO rrhh.categorias_laborales
    (nombre_categoria, codigo_categoria, departamento, nivel_jerarquico, descripcion, usuario_creacion)
    VALUES
    ('Administrativo Junior', 'ADM-001', 'Administración', 'Junior', 'Personal administrativo de nivel inicial', 'SISTEMA'),
    ('Administrativo Senior', 'ADM-002', 'Administración', 'Senior', 'Personal administrativo con experiencia', 'SISTEMA'),
    ('Supervisor Administrativo', 'ADM-003', 'Administración', 'Supervisor', 'Supervisor del área administrativa', 'SISTEMA'),
    ('Operario Producción', 'PROD-001', 'Producción', 'Operario', 'Operario de línea de producción', 'SISTEMA'),
    ('Técnico Especializado', 'PROD-002', 'Producción', 'Técnico', 'Técnico especializado en procesos', 'SISTEMA'),
    ('Supervisor Producción', 'PROD-003', 'Producción', 'Supervisor', 'Supervisor de área de producción', 'SISTEMA'),
    ('Vendedor', 'VEN-001', 'Ventas', 'Ejecutivo', 'Ejecutivo de ventas', 'SISTEMA'),
    ('Jefe de Ventas', 'VEN-002', 'Ventas', 'Jefe', 'Jefe del área de ventas', 'SISTEMA'),
    ('Gerente', 'GER-001', 'Gerencia', 'Gerente', 'Gerente de área', 'SISTEMA'),
    ('Director', 'DIR-001', 'Dirección', 'Director', 'Director ejecutivo', 'SISTEMA')

    PRINT '✅ Categorías laborales básicas insertadas exitosamente'
END
ELSE
    PRINT '⚠️ Las categorías laborales básicas ya existen'
GO

-- ============================================================================
-- VISTAS ÚTILES PARA REPORTES
-- ============================================================================

-- Vista: Empleados con información completa actual
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'vw_empleados_completo')
BEGIN
    EXEC('
    CREATE VIEW rrhh.vw_empleados_completo AS
    SELECT
        e.id,
        e.nombre_completo,
        e.dni_cuit,
        e.legajo_numero,
        e.fecha_ingreso,
        e.estado_actual,
        DATEDIFF(YEAR, e.fecha_ingreso, GETDATE()) as antiguedad_anos,

        -- Categoría actual (último contrato activo)
        c.nombre_categoria,
        c.departamento,
        c.nivel_jerarquico,

        -- Contacto
        e.telefono_principal,
        e.email_corporativo,

        -- Salario actual (último registro)
        (SELECT TOP 1 salario_nuevo
         FROM rrhh.historial_salarial h
         WHERE h.empleado_id = e.id
         ORDER BY h.fecha_efectiva DESC) as salario_actual,

        -- Última evaluación
        (SELECT TOP 1 puntaje_general
         FROM rrhh.evaluaciones_desempeno ev
         WHERE ev.empleado_id = e.id AND ev.estado_evaluacion = ''finalizada''
         ORDER BY ev.fecha_evaluacion DESC) as ultima_evaluacion,

        e.fecha_creacion,
        e.activo
    FROM rrhh.empleados e
    LEFT JOIN rrhh.contratos_laborales cl ON e.id = cl.empleado_id AND cl.estado_contrato = ''activo''
    LEFT JOIN rrhh.categorias_laborales c ON cl.categoria_id = c.id
    WHERE e.activo = 1
    ')
    PRINT '✅ Vista vw_empleados_completo creada exitosamente'
END
GO

PRINT ''
PRINT '🎉 ============================================================================'
PRINT '✅ ESTRUCTURA DE BASE DE DATOS DE RRHH CREADA EXITOSAMENTE'
PRINT '============================================================================'
PRINT '📊 Tablas creadas:'
PRINT '   • rrhh.empleados'
PRINT '   • rrhh.categorias_laborales'
PRINT '   • rrhh.contratos_laborales'
PRINT '   • rrhh.historial_categorias'
PRINT '   • rrhh.historial_salarial'
PRINT '   • rrhh.premios_reconocimientos'
PRINT '   • rrhh.sanciones_disciplinarias'
PRINT '   • rrhh.notificaciones_empleados'
PRINT '   • rrhh.evaluaciones_desempeno'
PRINT ''
PRINT '📋 Vistas creadas:'
PRINT '   • rrhh.vw_empleados_completo'
PRINT ''
PRINT '⚙️ Triggers de auditoría configurados'
PRINT '📝 Datos iniciales de categorías insertados'
PRINT '============================================================================'
