-- ==========================================================================
-- SCRIPT DE CREACIÓN DE TABLAS ADICIONALES - REXUS.APP
-- ==========================================================================
-- Fecha: 2025-01-15
-- Descripción: Crea todas las tablas adicionales requeridas para los módulos
--              de Recursos Humanos, Contabilidad, Mantenimiento y Logística
-- ==========================================================================

USE [inventario];
GO

-- ==========================================================================
-- 1. MÓDULO DE RECURSOS HUMANOS
-- ==========================================================================

-- 1.1 Tabla de empleados
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='empleados' AND xtype='U')
BEGIN
    CREATE TABLE empleados (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        apellido VARCHAR(100) NOT NULL,
        dni VARCHAR(20) UNIQUE NOT NULL,
        telefono VARCHAR(20),
        email VARCHAR(100),
        direccion VARCHAR(255),
        fecha_nacimiento DATE,
        fecha_ingreso DATE NOT NULL,
        salario_base DECIMAL(10,2) NOT NULL,
        cargo VARCHAR(100),
        departamento_id INT,
        estado VARCHAR(20) DEFAULT 'ACTIVO',
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla empleados creada';
END
ELSE
    PRINT '⚠️ Tabla empleados ya existe';

-- 1.2 Tabla de departamentos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='departamentos' AND xtype='U')
BEGIN
    CREATE TABLE departamentos (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(255),
        responsable VARCHAR(100),
        presupuesto_mensual DECIMAL(10,2) DEFAULT 0,
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla departamentos creada';
END
ELSE
    PRINT '⚠️ Tabla departamentos ya existe';

-- 1.3 Tabla de asistencias
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='asistencias' AND xtype='U')
BEGIN
    CREATE TABLE asistencias (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        fecha DATE NOT NULL,
        hora_entrada TIME,
        hora_salida TIME,
        horas_trabajadas DECIMAL(4,2) DEFAULT 0,
        horas_extra DECIMAL(4,2) DEFAULT 0,
        tipo VARCHAR(20) DEFAULT 'NORMAL', -- NORMAL, FALTA, VACACIONES, LICENCIA
        observaciones VARCHAR(255),
        fecha_registro DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla asistencias creada';
END
ELSE
    PRINT '⚠️ Tabla asistencias ya existe';

-- 1.4 Tabla de nómina
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='nomina' AND xtype='U')
BEGIN
    CREATE TABLE nomina (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        mes INT NOT NULL,
        anio INT NOT NULL,
        salario_base DECIMAL(10,2) NOT NULL,
        dias_trabajados INT DEFAULT 0,
        horas_extra DECIMAL(4,2) DEFAULT 0,
        bonos DECIMAL(10,2) DEFAULT 0,
        descuentos DECIMAL(10,2) DEFAULT 0,
        faltas INT DEFAULT 0,
        bruto DECIMAL(10,2) NOT NULL,
        total_descuentos DECIMAL(10,2) DEFAULT 0,
        neto DECIMAL(10,2) NOT NULL,
        fecha_calculo DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla nomina creada';
END
ELSE
    PRINT '⚠️ Tabla nomina ya existe';

-- 1.5 Tabla de bonos y descuentos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='bonos_descuentos' AND xtype='U')
BEGIN
    CREATE TABLE bonos_descuentos (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        tipo VARCHAR(20) NOT NULL, -- BONO, DESCUENTO
        concepto VARCHAR(255) NOT NULL,
        monto DECIMAL(10,2) NOT NULL,
        fecha_aplicacion DATE,
        mes_aplicacion INT,
        anio_aplicacion INT,
        estado VARCHAR(20) DEFAULT 'PENDIENTE', -- PENDIENTE, APLICADO, CANCELADO
        observaciones VARCHAR(255),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla bonos_descuentos creada';
END
ELSE
    PRINT '⚠️ Tabla bonos_descuentos ya existe';

-- 1.6 Tabla de historial laboral
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historial_laboral' AND xtype='U')
BEGIN
    CREATE TABLE historial_laboral (
        id INT PRIMARY KEY IDENTITY(1,1),
        empleado_id INT NOT NULL,
        tipo VARCHAR(50) NOT NULL, -- CONTRATACION, PROMOCION, CAMBIO_SALARIO, DESPIDO, etc.
        descripcion VARCHAR(255),
        fecha DATE DEFAULT GETDATE(),
        valor_anterior VARCHAR(100),
        valor_nuevo VARCHAR(100),
        usuario_creacion VARCHAR(50)
    );
    PRINT '✅ Tabla historial_laboral creada';
END
ELSE
    PRINT '⚠️ Tabla historial_laboral ya existe';

-- ==========================================================================
-- 2. MÓDULO DE CONTABILIDAD
-- ==========================================================================

-- 2.1 Tabla de libro contable
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='libro_contable' AND xtype='U')
BEGIN
    CREATE TABLE libro_contable (
        id INT PRIMARY KEY IDENTITY(1,1),
        numero_asiento INT NOT NULL,
        fecha_asiento DATE NOT NULL,
        tipo_asiento VARCHAR(50) NOT NULL, -- INGRESO, EGRESO, TRANSFERENCIA, AJUSTE
        concepto VARCHAR(255) NOT NULL,
        referencia VARCHAR(100),
        debe DECIMAL(12,2) DEFAULT 0,
        haber DECIMAL(12,2) DEFAULT 0,
        saldo DECIMAL(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'ACTIVO',
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla libro_contable creada';
END
ELSE
    PRINT '⚠️ Tabla libro_contable ya existe';

-- 2.2 Tabla de recibos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='recibos' AND xtype='U')
BEGIN
    CREATE TABLE recibos (
        id INT PRIMARY KEY IDENTITY(1,1),
        numero_recibo INT NOT NULL,
        fecha_emision DATE NOT NULL,
        tipo_recibo VARCHAR(50) NOT NULL, -- PAGO, COBRO, COMPROBANTE
        concepto VARCHAR(255) NOT NULL,
        beneficiario VARCHAR(255) NOT NULL,
        monto DECIMAL(12,2) NOT NULL,
        moneda VARCHAR(10) DEFAULT 'USD',
        estado VARCHAR(20) DEFAULT 'EMITIDO',
        impreso BIT DEFAULT 0,
        fecha_impresion DATETIME,
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla recibos creada';
END
ELSE
    PRINT '⚠️ Tabla recibos ya existe';

-- 2.3 Tabla de pagos por obra
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pagos_obra' AND xtype='U')
BEGIN
    CREATE TABLE pagos_obra (
        id INT PRIMARY KEY IDENTITY(1,1),
        obra_id INT NOT NULL,
        concepto VARCHAR(255) NOT NULL,
        categoria VARCHAR(100) NOT NULL, -- MATERIALES, MANO_OBRA, EQUIPOS, SERVICIOS
        monto DECIMAL(12,2) NOT NULL,
        fecha_pago DATE NOT NULL,
        metodo_pago VARCHAR(50) NOT NULL, -- EFECTIVO, TRANSFERENCIA, CHEQUE
        estado VARCHAR(20) DEFAULT 'PAGADO',
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE(),
        observaciones VARCHAR(255)
    );
    PRINT '✅ Tabla pagos_obra creada';
END
ELSE
    PRINT '⚠️ Tabla pagos_obra ya existe';

-- 2.4 Tabla de pagos de materiales
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pagos_materiales' AND xtype='U')
BEGIN
    CREATE TABLE pagos_materiales (
        id INT PRIMARY KEY IDENTITY(1,1),
        producto VARCHAR(255) NOT NULL,
        proveedor VARCHAR(255) NOT NULL,
        cantidad DECIMAL(10,2) NOT NULL,
        precio_unitario DECIMAL(10,2) NOT NULL,
        total DECIMAL(12,2) NOT NULL,
        pagado DECIMAL(12,2) DEFAULT 0,
        pendiente DECIMAL(12,2) DEFAULT 0,
        estado VARCHAR(20) DEFAULT 'PENDIENTE', -- PENDIENTE, PAGADO, PARCIAL
        fecha_compra DATE NOT NULL,
        fecha_pago DATE,
        usuario_creacion VARCHAR(50)
    );
    PRINT '✅ Tabla pagos_materiales creada';
END
ELSE
    PRINT '⚠️ Tabla pagos_materiales ya existe';

-- ==========================================================================
-- 3. MÓDULO DE MANTENIMIENTO
-- ==========================================================================

-- 3.1 Tabla de equipos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='equipos' AND xtype='U')
BEGIN
    CREATE TABLE equipos (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        tipo VARCHAR(50) NOT NULL, -- MAQUINARIA, HERRAMIENTA, VEHICULO, INSTALACION
        modelo VARCHAR(100),
        marca VARCHAR(100),
        numero_serie VARCHAR(100),
        fecha_adquisicion DATE,
        fecha_instalacion DATE,
        ubicacion VARCHAR(100),
        estado VARCHAR(20) DEFAULT 'OPERATIVO', -- OPERATIVO, MANTENIMIENTO, AVERIADO, FUERA_SERVICIO
        valor_adquisicion DECIMAL(12,2) DEFAULT 0,
        vida_util_anos INT DEFAULT 0,
        ultima_revision DATE,
        proxima_revision DATE,
        observaciones VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla equipos creada';
END
ELSE
    PRINT '⚠️ Tabla equipos ya existe';

-- 3.2 Tabla de herramientas
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='herramientas' AND xtype='U')
BEGIN
    CREATE TABLE herramientas (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        tipo VARCHAR(50) NOT NULL, -- MANUAL, ELECTRICA, NEUMATICA, HIDRAULICA
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100),
        fecha_adquisicion DATE,
        ubicacion VARCHAR(100),
        estado VARCHAR(20) DEFAULT 'DISPONIBLE', -- DISPONIBLE, EN_USO, MANTENIMIENTO, AVERIADA
        valor_adquisicion DECIMAL(10,2) DEFAULT 0,
        vida_util_anos INT DEFAULT 0,
        observaciones VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla herramientas creada';
END
ELSE
    PRINT '⚠️ Tabla herramientas ya existe';

-- 3.3 Tabla de mantenimientos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='mantenimientos' AND xtype='U')
BEGIN
    CREATE TABLE mantenimientos (
        id INT PRIMARY KEY IDENTITY(1,1),
        equipo_id INT NOT NULL,
        tipo VARCHAR(20) NOT NULL, -- PREVENTIVO, CORRECTIVO, PREDICTIVO
        descripcion VARCHAR(255) NOT NULL,
        fecha_programada DATE NOT NULL,
        fecha_realizacion DATE,
        estado VARCHAR(20) DEFAULT 'PROGRAMADO', -- PROGRAMADO, EN_PROCESO, COMPLETADO, CANCELADO
        observaciones VARCHAR(255),
        costo_estimado DECIMAL(10,2) DEFAULT 0,
        costo_real DECIMAL(10,2) DEFAULT 0,
        responsable VARCHAR(100),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla mantenimientos creada';
END
ELSE
    PRINT '⚠️ Tabla mantenimientos ya existe';

-- 3.4 Tabla de programación de mantenimiento
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='programacion_mantenimiento' AND xtype='U')
BEGIN
    CREATE TABLE programacion_mantenimiento (
        id INT PRIMARY KEY IDENTITY(1,1),
        equipo_id INT NOT NULL,
        tipo_mantenimiento VARCHAR(20) NOT NULL,
        frecuencia_dias INT NOT NULL,
        ultima_fecha DATE,
        proxima_fecha DATE,
        activo BIT DEFAULT 1,
        observaciones VARCHAR(255),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla programacion_mantenimiento creada';
END
ELSE
    PRINT '⚠️ Tabla programacion_mantenimiento ya existe';

-- 3.5 Tabla de tipos de mantenimiento
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tipos_mantenimiento' AND xtype='U')
BEGIN
    CREATE TABLE tipos_mantenimiento (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nombre VARCHAR(100) NOT NULL,
        descripcion VARCHAR(255),
        frecuencia_default_dias INT DEFAULT 30,
        activo BIT DEFAULT 1
    );
    PRINT '✅ Tabla tipos_mantenimiento creada';
END
ELSE
    PRINT '⚠️ Tabla tipos_mantenimiento ya existe';

-- 3.6 Tabla de estado de equipos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='estado_equipos' AND xtype='U')
BEGIN
    CREATE TABLE estado_equipos (
        id INT PRIMARY KEY IDENTITY(1,1),
        equipo_id INT NOT NULL,
        estado VARCHAR(20) NOT NULL,
        fecha_cambio DATETIME DEFAULT GETDATE(),
        motivo VARCHAR(255),
        usuario VARCHAR(50),
        observaciones VARCHAR(255)
    );
    PRINT '✅ Tabla estado_equipos creada';
END
ELSE
    PRINT '⚠️ Tabla estado_equipos ya existe';

-- 3.7 Tabla de historial de mantenimiento
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='historial_mantenimiento' AND xtype='U')
BEGIN
    CREATE TABLE historial_mantenimiento (
        id INT PRIMARY KEY IDENTITY(1,1),
        equipo_id INT,
        mantenimiento_id INT,
        tipo VARCHAR(50) NOT NULL, -- ALTA, MODIFICACION, PROGRAMADO, COMPLETADO, CANCELADO
        descripcion VARCHAR(255),
        fecha DATETIME DEFAULT GETDATE(),
        usuario VARCHAR(50)
    );
    PRINT '✅ Tabla historial_mantenimiento creada';
END
ELSE
    PRINT '⚠️ Tabla historial_mantenimiento ya existe';

-- ==========================================================================
-- 4. MÓDULO DE LOGÍSTICA
-- ==========================================================================

-- 4.1 Tabla de transportes
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='transportes' AND xtype='U')
BEGIN
    CREATE TABLE transportes (
        id INT PRIMARY KEY IDENTITY(1,1),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        tipo VARCHAR(50) NOT NULL, -- PROPIO, TERCERIZADO, COURIER
        proveedor VARCHAR(100),
        capacidad_kg DECIMAL(10,2),
        capacidad_m3 DECIMAL(10,2),
        costo_km DECIMAL(8,2),
        disponible BIT DEFAULT 1,
        observaciones VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla transportes creada';
END
ELSE
    PRINT '⚠️ Tabla transportes ya existe';

-- 4.2 Tabla de entregas
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='entregas' AND xtype='U')
BEGIN
    CREATE TABLE entregas (
        id INT PRIMARY KEY IDENTITY(1,1),
        obra_id INT NOT NULL,
        transporte_id INT,
        fecha_programada DATE NOT NULL,
        fecha_entrega DATE,
        direccion_entrega VARCHAR(255) NOT NULL,
        contacto VARCHAR(100),
        telefono VARCHAR(20),
        estado VARCHAR(20) DEFAULT 'PROGRAMADA', -- PROGRAMADA, EN_TRANSITO, ENTREGADA, CANCELADA
        observaciones VARCHAR(255),
        costo_envio DECIMAL(10,2) DEFAULT 0,
        usuario_creacion VARCHAR(50),
        fecha_creacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla entregas creada';
END
ELSE
    PRINT '⚠️ Tabla entregas ya existe';

-- 4.3 Tabla de detalle de entregas
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_entregas' AND xtype='U')
BEGIN
    CREATE TABLE detalle_entregas (
        id INT PRIMARY KEY IDENTITY(1,1),
        entrega_id INT NOT NULL,
        producto VARCHAR(100) NOT NULL,
        cantidad DECIMAL(10,2) NOT NULL,
        peso_kg DECIMAL(10,2),
        volumen_m3 DECIMAL(10,2),
        observaciones VARCHAR(255)
    );
    PRINT '✅ Tabla detalle_entregas creada';
END
ELSE
    PRINT '⚠️ Tabla detalle_entregas ya existe';

-- ==========================================================================
-- 5. CONFIGURACIÓN Y AUDITORÍA (AMPLIADO)
-- ==========================================================================

-- 5.1 Tabla de configuración del sistema
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='configuracion_sistema' AND xtype='U')
BEGIN
    CREATE TABLE configuracion_sistema (
        id INT PRIMARY KEY IDENTITY(1,1),
        categoria VARCHAR(50) NOT NULL, -- GENERAL, SEGURIDAD, NOTIFICACIONES, REPORTES
        clave VARCHAR(100) NOT NULL,
        valor VARCHAR(255),
        tipo_dato VARCHAR(20) DEFAULT 'TEXT', -- TEXT, NUMBER, BOOLEAN, DATE, JSON
        descripcion VARCHAR(255),
        valor_default VARCHAR(255),
        modificable BIT DEFAULT 1,
        fecha_modificacion DATETIME DEFAULT GETDATE(),
        usuario_modificacion VARCHAR(50)
    );
    PRINT '✅ Tabla configuracion_sistema creada';
END
ELSE
    PRINT '⚠️ Tabla configuracion_sistema ya existe';

-- 5.2 Tabla de parámetros por módulos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='parametros_modulos' AND xtype='U')
BEGIN
    CREATE TABLE parametros_modulos (
        id INT PRIMARY KEY IDENTITY(1,1),
        modulo VARCHAR(50) NOT NULL, -- INVENTARIO, OBRAS, COMPRAS, etc.
        parametro VARCHAR(100) NOT NULL,
        valor VARCHAR(255),
        tipo VARCHAR(20) DEFAULT 'TEXT',
        descripcion VARCHAR(255),
        activo BIT DEFAULT 1,
        fecha_creacion DATETIME DEFAULT GETDATE(),
        fecha_modificacion DATETIME DEFAULT GETDATE()
    );
    PRINT '✅ Tabla parametros_modulos creada';
END
ELSE
    PRINT '⚠️ Tabla parametros_modulos ya existe';

-- 5.3 Tabla de auditoría de cambios
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='auditoria_cambios' AND xtype='U')
BEGIN
    CREATE TABLE auditoria_cambios (
        id INT PRIMARY KEY IDENTITY(1,1),
        tabla VARCHAR(50) NOT NULL,
        registro_id INT NOT NULL,
        operacion VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
        campo VARCHAR(50),
        valor_anterior VARCHAR(255),
        valor_nuevo VARCHAR(255),
        usuario VARCHAR(50),
        fecha DATETIME DEFAULT GETDATE(),
        ip_address VARCHAR(45),
        user_agent VARCHAR(255)
    );
    PRINT '✅ Tabla auditoria_cambios creada';
END
ELSE
    PRINT '⚠️ Tabla auditoria_cambios ya existe';

-- 5.4 Tabla de logs del sistema
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='logs_sistema' AND xtype='U')
BEGIN
    CREATE TABLE logs_sistema (
        id INT PRIMARY KEY IDENTITY(1,1),
        nivel VARCHAR(20) NOT NULL, -- ERROR, WARNING, INFO, DEBUG
        modulo VARCHAR(50) NOT NULL,
        mensaje VARCHAR(500) NOT NULL,
        detalle TEXT,
        usuario VARCHAR(50),
        fecha DATETIME DEFAULT GETDATE(),
        ip_address VARCHAR(45),
        stack_trace TEXT
    );
    PRINT '✅ Tabla logs_sistema creada';
END
ELSE
    PRINT '⚠️ Tabla logs_sistema ya existe';

-- ==========================================================================
-- 6. ÍNDICES PARA OPTIMIZACIÓN
-- ==========================================================================

-- Índices para Recursos Humanos
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_empleados_departamento')
    CREATE INDEX IX_empleados_departamento ON empleados(departamento_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_empleados_estado')
    CREATE INDEX IX_empleados_estado ON empleados(estado);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_asistencias_empleado_fecha')
    CREATE INDEX IX_asistencias_empleado_fecha ON asistencias(empleado_id, fecha);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_nomina_empleado_periodo')
    CREATE INDEX IX_nomina_empleado_periodo ON nomina(empleado_id, anio, mes);

-- Índices para Contabilidad
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_libro_contable_fecha')
    CREATE INDEX IX_libro_contable_fecha ON libro_contable(fecha_asiento);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_libro_contable_tipo')
    CREATE INDEX IX_libro_contable_tipo ON libro_contable(tipo_asiento);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_recibos_fecha')
    CREATE INDEX IX_recibos_fecha ON recibos(fecha_emision);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pagos_obra_obra')
    CREATE INDEX IX_pagos_obra_obra ON pagos_obra(obra_id);

-- Índices para Mantenimiento
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_equipos_estado')
    CREATE INDEX IX_equipos_estado ON equipos(estado);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_mantenimientos_equipo')
    CREATE INDEX IX_mantenimientos_equipo ON mantenimientos(equipo_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_mantenimientos_fecha')
    CREATE INDEX IX_mantenimientos_fecha ON mantenimientos(fecha_programada);

-- Índices para Logística
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_entregas_obra')
    CREATE INDEX IX_entregas_obra ON entregas(obra_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_entregas_fecha')
    CREATE INDEX IX_entregas_fecha ON entregas(fecha_programada);

-- Índices para Auditoría
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_cambios_tabla')
    CREATE INDEX IX_auditoria_cambios_tabla ON auditoria_cambios(tabla, registro_id);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_auditoria_cambios_fecha')
    CREATE INDEX IX_auditoria_cambios_fecha ON auditoria_cambios(fecha);

PRINT '✅ Índices de optimización creados';

-- ==========================================================================
-- 7. DATOS INICIALES
-- ==========================================================================

-- Departamentos básicos
IF NOT EXISTS (SELECT * FROM departamentos WHERE codigo = 'ADMIN')
BEGIN
    INSERT INTO departamentos (codigo, nombre, descripcion) VALUES
    ('ADMIN', 'Administración', 'Departamento administrativo'),
    ('PROD', 'Producción', 'Departamento de producción'),
    ('MANT', 'Mantenimiento', 'Departamento de mantenimiento'),
    ('COMP', 'Compras', 'Departamento de compras'),
    ('VENT', 'Ventas', 'Departamento de ventas');
    PRINT '✅ Departamentos básicos insertados';
END
ELSE
    PRINT '⚠️ Departamentos básicos ya existen';

-- Tipos de mantenimiento
IF NOT EXISTS (SELECT * FROM tipos_mantenimiento WHERE codigo = 'PREV_BASIC')
BEGIN
    INSERT INTO tipos_mantenimiento (codigo, nombre, descripcion, frecuencia_default_dias) VALUES
    ('PREV_BASIC', 'Mantenimiento Preventivo Básico', 'Revisión básica de funcionamiento', 30),
    ('PREV_COMPLETO', 'Mantenimiento Preventivo Completo', 'Revisión completa del equipo', 90),
    ('CORR_MENOR', 'Mantenimiento Correctivo Menor', 'Reparación menor', 0),
    ('CORR_MAYOR', 'Mantenimiento Correctivo Mayor', 'Reparación mayor', 0),
    ('PRED_VIBR', 'Mantenimiento Predictivo por Vibración', 'Análisis de vibraciones', 60);
    PRINT '✅ Tipos de mantenimiento insertados';
END
ELSE
    PRINT '⚠️ Tipos de mantenimiento ya existen';

-- Configuración del sistema
IF NOT EXISTS (SELECT * FROM configuracion_sistema WHERE clave = 'EMPRESA_NOMBRE')
BEGIN
    INSERT INTO configuracion_sistema (categoria, clave, valor, tipo_dato, descripcion) VALUES
    ('GENERAL', 'EMPRESA_NOMBRE', 'Rexus S.A.', 'TEXT', 'Nombre de la empresa'),
    ('GENERAL', 'EMPRESA_RUT', '', 'TEXT', 'RUT de la empresa'),
    ('RRHH', 'HORAS_TRABAJO_DIA', '8', 'NUMBER', 'Horas de trabajo por día'),
    ('RRHH', 'DIAS_TRABAJO_SEMANA', '5', 'NUMBER', 'Días de trabajo por semana'),
    ('MANTENIMIENTO', 'DIAS_ALERTA_VENCIMIENTO', '7', 'NUMBER', 'Días de alerta antes del vencimiento'),
    ('CONTABILIDAD', 'MONEDA_DEFAULT', 'USD', 'TEXT', 'Moneda por defecto');
    PRINT '✅ Configuración del sistema insertada';
END
ELSE
    PRINT '⚠️ Configuración del sistema ya existe';

-- ==========================================================================
-- FINALIZACIÓN
-- ==========================================================================

PRINT '';
PRINT '🎉 ¡CREACIÓN DE TABLAS ADICIONALES COMPLETADA!';
PRINT '===============================================';
PRINT 'Se han creado todas las tablas necesarias para:';
PRINT '  ✅ Módulo de Recursos Humanos (6 tablas)';
PRINT '  ✅ Módulo de Contabilidad (4 tablas)';
PRINT '  ✅ Módulo de Mantenimiento (7 tablas)';
PRINT '  ✅ Módulo de Logística (3 tablas)';
PRINT '  ✅ Configuración y Auditoría (4 tablas)';
PRINT '  ✅ Índices de optimización';
PRINT '  ✅ Datos iniciales básicos';
PRINT '';
PRINT 'Total: 24 nuevas tablas creadas';
PRINT 'El sistema está listo para usar todas las funcionalidades implementadas.';
PRINT '===============================================';

GO