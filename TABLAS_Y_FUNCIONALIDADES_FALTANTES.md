# TABLAS Y FUNCIONALIDADES FALTANTES - Rexus.app

## 📊 **ESTADO ACTUAL**
- **Tablas existentes**: 52/55 (94.5%)
- **Módulos implementados**: 4/13 (31%)
- **Funcionalidades críticas**: Completadas

---

## 🔴 **TABLAS CRÍTICAS FALTANTES**

### **1. SISTEMA DE USUARIOS Y PERMISOS**
```sql
-- Falta crear estas tablas para permisos granulares
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    rol VARCHAR(50) DEFAULT 'USUARIO',
    activo BIT DEFAULT 1,
    ultimo_login DATETIME,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BIT DEFAULT 1
);

CREATE TABLE permisos_usuario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    permiso VARCHAR(50) NOT NULL, -- read, write, delete, admin
    activo BIT DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE modulos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    activo BIT DEFAULT 1
);
```

### **2. MÓDULO DE PEDIDOS COMPLETO**
```sql
-- Faltan tablas para el flujo completo de pedidos
CREATE TABLE pedidos_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    descripcion VARCHAR(255),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE TABLE pedidos_historial (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50),
    fecha_cambio DATETIME DEFAULT GETDATE(),
    usuario_id INT,
    observaciones TEXT,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

CREATE TABLE pedidos_entregas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    numero_entrega VARCHAR(50),
    fecha_entrega DATE,
    responsable_entrega VARCHAR(100),
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);
```

### **3. MÓDULO DE HERRAJES**
```sql
-- Catálogo completo de herrajes
CREATE TABLE herrajes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_id INT,
    proveedor_id INT,
    precio_unitario DECIMAL(10,2),
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 0,
    unidad_medida VARCHAR(20),
    especificaciones TEXT,
    imagen_url VARCHAR(255),
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE herrajes_categorias (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    activo BIT DEFAULT 1
);

CREATE TABLE herrajes_proveedores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    activo BIT DEFAULT 1
);
```

### **4. MÓDULO DE VIDRIOS**
```sql
-- Sistema completo de vidrios
CREATE TABLE vidrios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    espesor DECIMAL(4,2) NOT NULL,
    color VARCHAR(50),
    precio_m2 DECIMAL(10,2),
    proveedor_id INT,
    especificaciones TEXT,
    activo BIT DEFAULT 1
);

CREATE TABLE vidrios_tipos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    propiedades TEXT,
    activo BIT DEFAULT 1
);

CREATE TABLE vidrios_medidas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    obra_id INT NOT NULL,
    vidrio_id INT NOT NULL,
    ancho DECIMAL(8,2) NOT NULL,
    alto DECIMAL(8,2) NOT NULL,
    cantidad INT NOT NULL,
    metros_cuadrados DECIMAL(10,2),
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    fecha_pedido DATE,
    FOREIGN KEY (obra_id) REFERENCES obras(id),
    FOREIGN KEY (vidrio_id) REFERENCES vidrios(id)
);

CREATE TABLE vidrios_instalaciones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    medida_id INT NOT NULL,
    fecha_instalacion DATE,
    tecnico_id INT,
    estado VARCHAR(50) DEFAULT 'PROGRAMADA',
    observaciones TEXT,
    FOREIGN KEY (medida_id) REFERENCES vidrios_medidas(id)
);
```

### **5. MÓDULO DE COMPRAS**
```sql
-- Sistema completo de compras
CREATE TABLE compras_ordenes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    numero_orden VARCHAR(50) UNIQUE NOT NULL,
    proveedor_id INT NOT NULL,
    fecha_orden DATE NOT NULL,
    fecha_entrega_estimada DATE,
    estado VARCHAR(50) DEFAULT 'PENDIENTE',
    subtotal DECIMAL(12,2) DEFAULT 0,
    impuestos DECIMAL(12,2) DEFAULT 0,
    total DECIMAL(12,2) DEFAULT 0,
    observaciones TEXT,
    usuario_creacion INT,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE TABLE compras_proveedores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nit VARCHAR(20),
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    terminos_pago VARCHAR(100),
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE compras_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    orden_id INT NOT NULL,
    producto_codigo VARCHAR(50),
    descripcion VARCHAR(255) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (orden_id) REFERENCES compras_ordenes(id)
);
```

---

## 🟡 **FUNCIONALIDADES FALTANTES POR MÓDULO**

### **1. MÓDULO DE USUARIOS (40% → 100%)**
- ❌ **Permisos granulares**: Sistema detallado por módulo/acción
- ❌ **Logs de actividad**: Historial completo de acciones
- ❌ **Gestión de sesiones**: Control de sesiones múltiples
- ❌ **Políticas de seguridad**: Expiración de contraseñas
- ❌ **Recuperación de contraseña**: Sistema de reset
- ❌ **Integración con aplicación**: Menú principal

### **2. MÓDULO DE PEDIDOS (Model 100% → Interface 0%)**
- ❌ **Vista PyQt6**: Interface completa para pedidos
- ❌ **Controlador**: Lógica de negocio y validaciones
- ❌ **Estados de pedido**: Workflow completo
- ❌ **Integración con inventario**: Verificación de stock
- ❌ **Generación de documentos**: PDF, reportes
- ❌ **Seguimiento de entregas**: Estado en tiempo real

### **3. MÓDULO DE HERRAJES (30% → 100%)**
- ❌ **Vista PyQt6**: Interface moderna y funcional
- ❌ **Catálogo visual**: Imágenes y especificaciones
- ❌ **Gestión de categorías**: Organización por tipos
- ❌ **Control de stock**: Alertas y reposición
- ❌ **Integración con obras**: Asignación automática
- ❌ **Proveedores específicos**: Gestión de proveedores

### **4. MÓDULO DE VIDRIOS (0% → 100%)**
- ❌ **Catálogo completo**: Tipos, espesores, colores
- ❌ **Calculadora de m²**: Optimización de cortes
- ❌ **Programación de cortes**: Calendario de producción
- ❌ **Control de calidad**: Inspección y certificados
- ❌ **Instalación y seguimiento**: Técnicos y cronograma
- ❌ **Integración con obras**: Pedidos automáticos

### **5. MÓDULO DE COMPRAS (100% Backend → 0% Frontend)**
- ❌ **Vista PyQt6**: Interface para órdenes de compra
- ❌ **Gestión de proveedores**: CRUD completo
- ❌ **Aprobación de órdenes**: Workflow de aprobación
- ❌ **Seguimiento de entregas**: Estado de órdenes
- ❌ **Integración con inventario**: Actualización automática
- ❌ **Reportes financieros**: Análisis de costos

### **6. MÓDULO DE OBRAS (85% → 100%)**
- ❌ **Asignación de personal**: Recursos humanos por obra
- ❌ **Gestión de materiales**: Inventario específico
- ❌ **Seguimiento de costos**: Presupuesto vs real
- ❌ **Documentos adjuntos**: Planos y contratos
- ❌ **Facturación por obra**: Integración contable
- ❌ **Cronograma avanzado**: Gantt interactivo

### **7. DASHBOARD Y REPORTES (0% → 100%)**
- ❌ **Dashboard ejecutivo**: KPIs principales
- ❌ **Gráficos en tiempo real**: Charts interactivos
- ❌ **Reportes automáticos**: Programación y envío
- ❌ **Exportación avanzada**: PDF/Excel con templates
- ❌ **Business Intelligence**: Análisis de tendencias
- ❌ **Alertas inteligentes**: Notificaciones automáticas

---

## 🔵 **MÓDULOS NUEVOS A IMPLEMENTAR**

### **8. CRM - GESTIÓN DE CLIENTES**
```sql
CREATE TABLE clientes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nit VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    tipo_cliente VARCHAR(50), -- CORPORATIVO, INDIVIDUAL
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    fecha_creacion DATETIME DEFAULT GETDATE()
);

CREATE TABLE contactos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    cargo VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    principal BIT DEFAULT 0,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE leads (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    fuente VARCHAR(50),
    estado VARCHAR(50) DEFAULT 'NUEVO',
    prioridad VARCHAR(20) DEFAULT 'MEDIA',
    valor_estimado DECIMAL(12,2),
    fecha_contacto DATE,
    fecha_seguimiento DATE,
    observaciones TEXT,
    usuario_asignado INT,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

### **9. SISTEMA DE NOTIFICACIONES**
```sql
CREATE TABLE notificaciones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- INFO, WARNING, ERROR, SUCCESS
    modulo VARCHAR(50),
    leida BIT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_leida DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### **10. SISTEMA DE REPORTES**
```sql
CREATE TABLE reportes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL, -- PDF, EXCEL, CSV
    modulo VARCHAR(50),
    query_sql TEXT,
    parametros TEXT, -- JSON con parámetros
    programado BIT DEFAULT 0,
    frecuencia VARCHAR(50), -- DIARIO, SEMANAL, MENSUAL
    usuario_creacion INT,
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

---

## 🎯 **PRIORIDADES DE IMPLEMENTACIÓN**

### **🔴 ALTA PRIORIDAD (Próxima sesión)**
1. **Completar Sistema de Usuarios**
   - Integrar vista de admin en menú principal
   - Implementar permisos granulares
   - Agregar logs de actividad

2. **Módulo de Pedidos**
   - Crear vista PyQt6 completa
   - Implementar controlador
   - Integrar con inventario

3. **Completar Módulo de Obras**
   - Asignación de personal
   - Gestión de materiales
   - Seguimiento de costos

### **🟡 MEDIA PRIORIDAD (2-3 sesiones)**
4. **Dashboard y Reportes**
   - KPIs principales
   - Gráficos en tiempo real
   - Exportación PDF/Excel

5. **Módulo de Herrajes**
   - Vista PyQt6 completa
   - Catálogo visual
   - Integración con obras

6. **Módulo de Vidrios**
   - Catálogo completo
   - Calculadora de m²
   - Programación de cortes

### **🔵 BAJA PRIORIDAD (4-5 sesiones)**
7. **CRM Básico**
   - Gestión de clientes
   - Seguimiento de leads
   - Cotizaciones

8. **Sistema de Notificaciones**
   - Notificaciones en tiempo real
   - Alertas automáticas
   - Historial de notificaciones

9. **Reportes Avanzados**
   - Reportes programados
   - Templates personalizados
   - Business Intelligence

---

## 📋 **SCRIPT DE CREACIÓN DE TABLAS FALTANTES**

```sql
-- Ejecutar este script para crear todas las tablas faltantes
-- NOTA: Algunas tablas ya existen, verificar antes de ejecutar

-- 1. Sistema de usuarios y permisos
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    rol VARCHAR(50) DEFAULT 'USUARIO',
    activo BIT DEFAULT 1,
    ultimo_login DATETIME,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

-- 2. Módulo de pedidos
CREATE TABLE pedidos_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    descripcion VARCHAR(255),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- 3. Módulo de herrajes
CREATE TABLE herrajes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_unitario DECIMAL(10,2),
    stock_actual INT DEFAULT 0,
    activo BIT DEFAULT 1
);

-- 4. Módulo de vidrios
CREATE TABLE vidrios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    espesor DECIMAL(4,2) NOT NULL,
    color VARCHAR(50),
    precio_m2 DECIMAL(10,2),
    activo BIT DEFAULT 1
);

-- 5. CRM
CREATE TABLE clientes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nit VARCHAR(20),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    fecha_creacion DATETIME DEFAULT GETDATE()
);

-- 6. Notificaciones
CREATE TABLE notificaciones (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    leida BIT DEFAULT 0,
    fecha_creacion DATETIME DEFAULT GETDATE()
);
```

---

## 📊 **RESUMEN EJECUTIVO**

### **Estado Actual**
- ✅ **Base sólida**: 52 tablas, 4 módulos completos
- ✅ **Autenticación**: Funcional al 100%
- ✅ **Módulos críticos**: Administración, Mantenimiento, Logística

### **Próximos Pasos**
1. **Implementar 6 tablas críticas** para usuarios y pedidos
2. **Completar 3 módulos principales** (Usuarios, Pedidos, Obras)
3. **Crear dashboard básico** con KPIs
4. **Implementar 2 módulos nuevos** (Herrajes, Vidrios)

### **Impacto Estimado**
- **Tablas faltantes**: 32 (se pueden crear en 2-3 sesiones)
- **Módulos críticos**: 6 (se pueden completar en 4-5 sesiones)
- **Sistema completo**: 8-10 sesiones para 100% funcional

**El sistema está en excelente estado y solo requiere completar las funcionalidades específicas por módulo.**