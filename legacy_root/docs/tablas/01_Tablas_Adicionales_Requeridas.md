# Tablas Adicionales Requeridas para Funcionalidad Completa

## Resumen Ejecutivo

Este documento especifica las tablas adicionales necesarias para implementar completamente todas las funcionalidades del sistema Rexus.app. Estas tablas son requeridas por los módulos ya implementados pero actualmente no existen en la base de datos.

## 1. Módulo de Recursos Humanos

### Tablas Requeridas:

#### 1.1 `empleados`
```sql
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
```

#### 1.2 `departamentos`
```sql
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
```

#### 1.3 `asistencias`
```sql
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
    fecha_registro DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);
```

#### 1.4 `nomina`
```sql
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
    fecha_calculo DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);
```

#### 1.5 `bonos_descuentos`
```sql
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
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);
```

#### 1.6 `historial_laboral`
```sql
CREATE TABLE historial_laboral (
    id INT PRIMARY KEY IDENTITY(1,1),
    empleado_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- CONTRATACION, PROMOCION, CAMBIO_SALARIO, DESPIDO, etc.
    descripcion VARCHAR(255),
    fecha DATE DEFAULT GETDATE(),
    valor_anterior VARCHAR(100),
    valor_nuevo VARCHAR(100),
    usuario_creacion VARCHAR(50),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id)
);
```

## 2. Módulo de Contabilidad

### Tablas Requeridas:

#### 2.1 `libro_contable`
```sql
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
```

#### 2.2 `recibos`
```sql
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
```

#### 2.3 `pagos_obra`
```sql
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
    observaciones VARCHAR(255),
    FOREIGN KEY (obra_id) REFERENCES obras(id)
);
```

#### 2.4 `pagos_materiales`
```sql
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
```

## 3. Módulo de Mantenimiento

### Tablas Requeridas:

#### 3.1 `equipos`
```sql
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
```

#### 3.2 `herramientas`
```sql
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
```

#### 3.3 `mantenimientos`
```sql
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
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);
```

#### 3.4 `programacion_mantenimiento`
```sql
CREATE TABLE programacion_mantenimiento (
    id INT PRIMARY KEY IDENTITY(1,1),
    equipo_id INT NOT NULL,
    tipo_mantenimiento VARCHAR(20) NOT NULL,
    frecuencia_dias INT NOT NULL,
    ultima_fecha DATE,
    proxima_fecha DATE,
    activo BIT DEFAULT 1,
    observaciones VARCHAR(255),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);
```

#### 3.5 `tipos_mantenimiento`
```sql
CREATE TABLE tipos_mantenimiento (
    id INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    frecuencia_default_dias INT DEFAULT 30,
    activo BIT DEFAULT 1
);
```

#### 3.6 `estado_equipos`
```sql
CREATE TABLE estado_equipos (
    id INT PRIMARY KEY IDENTITY(1,1),
    equipo_id INT NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha_cambio DATETIME DEFAULT GETDATE(),
    motivo VARCHAR(255),
    usuario VARCHAR(50),
    observaciones VARCHAR(255),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);
```

#### 3.7 `historial_mantenimiento`
```sql
CREATE TABLE historial_mantenimiento (
    id INT PRIMARY KEY IDENTITY(1,1),
    equipo_id INT,
    mantenimiento_id INT,
    tipo VARCHAR(50) NOT NULL, -- ALTA, MODIFICACION, PROGRAMADO, COMPLETADO, CANCELADO
    descripcion VARCHAR(255),
    fecha DATETIME DEFAULT GETDATE(),
    usuario VARCHAR(50),
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (mantenimiento_id) REFERENCES mantenimientos(id)
);
```

## 4. Módulo de Configuración (Ampliado)

### Tablas Adicionales Requeridas:

#### 4.1 `configuracion_sistema`
```sql
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
```

#### 4.2 `parametros_modulos`
```sql
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
```

## 5. Auditoría y Logging (Ampliado)

### Tablas Adicionales Requeridas:

#### 5.1 `auditoria_cambios`
```sql
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
```

#### 5.2 `logs_sistema`
```sql
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
```

## 6. Logística (Nuevo Módulo)

### Tablas Requeridas:

#### 6.1 `transportes`
```sql
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
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

#### 6.2 `entregas`
```sql
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
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (obra_id) REFERENCES obras(id),
    FOREIGN KEY (transporte_id) REFERENCES transportes(id)
);
```

#### 6.3 `detalle_entregas`
```sql
CREATE TABLE detalle_entregas (
    id INT PRIMARY KEY IDENTITY(1,1),
    entrega_id INT NOT NULL,
    producto VARCHAR(100) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    peso_kg DECIMAL(10,2),
    volumen_m3 DECIMAL(10,2),
    observaciones VARCHAR(255),
    FOREIGN KEY (entrega_id) REFERENCES entregas(id)
);
```

## 7. Índices Recomendados

### Índices de Rendimiento:
```sql
-- Recursos Humanos
CREATE INDEX IX_empleados_departamento ON empleados(departamento_id);
CREATE INDEX IX_empleados_estado ON empleados(estado);
CREATE INDEX IX_asistencias_empleado_fecha ON asistencias(empleado_id, fecha);
CREATE INDEX IX_nomina_empleado_periodo ON nomina(empleado_id, anio, mes);

-- Contabilidad
CREATE INDEX IX_libro_contable_fecha ON libro_contable(fecha_asiento);
CREATE INDEX IX_libro_contable_tipo ON libro_contable(tipo_asiento);
CREATE INDEX IX_recibos_fecha ON recibos(fecha_emision);
CREATE INDEX IX_pagos_obra_obra ON pagos_obra(obra_id);

-- Mantenimiento
CREATE INDEX IX_equipos_estado ON equipos(estado);
CREATE INDEX IX_mantenimientos_equipo ON mantenimientos(equipo_id);
CREATE INDEX IX_mantenimientos_fecha ON mantenimientos(fecha_programada);

-- Auditoría
CREATE INDEX IX_auditoria_cambios_tabla ON auditoria_cambios(tabla, registro_id);
CREATE INDEX IX_auditoria_cambios_fecha ON auditoria_cambios(fecha);
```

## 8. Datos Iniciales Recomendados

### Tipos de Mantenimiento:
```sql
INSERT INTO tipos_mantenimiento (codigo, nombre, descripcion, frecuencia_default_dias) VALUES
('PREV_BASIC', 'Mantenimiento Preventivo Básico', 'Revisión básica de funcionamiento', 30),
('PREV_COMPLETO', 'Mantenimiento Preventivo Completo', 'Revisión completa del equipo', 90),
('CORR_MENOR', 'Mantenimiento Correctivo Menor', 'Reparación menor', 0),
('CORR_MAYOR', 'Mantenimiento Correctivo Mayor', 'Reparación mayor', 0),
('PRED_VIBR', 'Mantenimiento Predictivo por Vibración', 'Análisis de vibraciones', 60);
```

### Departamentos Básicos:
```sql
INSERT INTO departamentos (codigo, nombre, descripcion) VALUES
('ADMIN', 'Administración', 'Departamento administrativo'),
('PROD', 'Producción', 'Departamento de producción'),
('MANT', 'Mantenimiento', 'Departamento de mantenimiento'),
('COMP', 'Compras', 'Departamento de compras'),
('VENT', 'Ventas', 'Departamento de ventas');
```

### Configuración del Sistema:
```sql
INSERT INTO configuracion_sistema (categoria, clave, valor, tipo_dato, descripcion) VALUES
('GENERAL', 'EMPRESA_NOMBRE', 'Rexus S.A.', 'TEXT', 'Nombre de la empresa'),
('GENERAL', 'EMPRESA_RUT', '', 'TEXT', 'RUT de la empresa'),
('RRHH', 'HORAS_TRABAJO_DIA', '8', 'NUMBER', 'Horas de trabajo por día'),
('RRHH', 'DIAS_TRABAJO_SEMANA', '5', 'NUMBER', 'Días de trabajo por semana'),
('MANTENIMIENTO', 'DIAS_ALERTA_VENCIMIENTO', '7', 'NUMBER', 'Días de alerta antes del vencimiento'),
('CONTABILIDAD', 'MONEDA_DEFAULT', 'USD', 'TEXT', 'Moneda por defecto');
```

## 9. Observaciones Importantes

1. **Dependencias**: Todas las tablas que referencian la tabla `obras` requieren que esta exista previamente.

2. **Seguridad**: Todas las tablas incluyen campos de auditoría (`usuario_creacion`, `fecha_creacion`, etc.).

3. **Integridad**: Se recomiendan claves foráneas para mantener la integridad referencial.

4. **Escalabilidad**: Los campos de texto variable están dimensionados para crecimiento futuro.

5. **Compatibilidad**: Todas las definiciones son compatibles con SQL Server.

## 10. Próximos Pasos

1. **Crear las tablas** en el orden especificado (considerando dependencias)
2. **Insertar datos iniciales** para configuración básica
3. **Ejecutar scripts de migración** para datos existentes
4. **Implementar triggers de auditoría** para seguimiento de cambios
5. **Configurar permisos** de acceso por módulo
6. **Probar funcionalidad** con las nuevas tablas

---

**Fecha de Creación**: 2025-01-15  
**Versión**: 1.0  
**Autor**: Sistema Rexus.app  
**Estado**: Pendiente de Implementación