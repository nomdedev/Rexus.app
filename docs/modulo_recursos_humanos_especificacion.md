# MÓDULO DE GESTIÓN DE RECURSOS HUMANOS Y CONTABILIDAD
## Especificación Técnica y Funcional

### DESCRIPCIÓN GENERAL
Sistema integral para la gestión de empleados que permitirá a contabilidad y RRHH manejar toda la información del personal de la empresa, desde datos básicos hasta historial laboral completo.

---

## FUNCIONALIDADES PRINCIPALES

### 1. GESTIÓN DE EMPLEADOS
#### Datos Básicos del Empleado
- **ID Único del Empleado** (autoincremental)
- **Información Personal:**
  - Nombre completo
  - DNI/CUIT
  - Fecha de nacimiento
  - Dirección completa
  - Teléfono(s) de contacto
  - Email personal y corporativo
  - Estado civil
  - Contacto de emergencia

#### Datos Laborales
- **Información Contractual:**
  - Fecha de ingreso
  - Tipo de contrato (indefinido, plazo fijo, prueba, temporal)
  - Estado actual (activo, período de prueba, suspendido, inactivo)
  - Fecha de finalización (si aplica)
  - Legajo número

### 2. SISTEMA DE CATEGORÍAS Y PUESTOS
#### Categorías Laborales
- **Categoría Actual:** Puesto/cargo específico
- **Departamento/Área:** (Producción, Administración, Ventas, etc.)
- **Nivel Jerárquico:** (Operario, Supervisor, Jefe, Gerente, Director)
- **Modalidad:** (Presencial, remoto, híbrido)

#### Historial de Categorías
- **Registro de Cambios:**
  - Fecha del cambio
  - Categoría anterior
  - Categoría nueva
  - Motivo del cambio
  - Usuario que autorizó el cambio
  - Observaciones

### 3. GESTIÓN SALARIAL
#### Información Salarial
- **Salario Base Actual**
- **Fecha de último aumento**
- **Historial Salarial:**
  - Fecha de cambio
  - Salario anterior
  - Salario nuevo
  - Motivo del ajuste
  - Porcentaje de aumento

#### Componentes Adicionales
- **Bonificaciones fijas** (antigüedad, título, etc.)
- **Descuentos fijos** (obra social, sindicato, etc.)
- **Variables mensuales** (horas extra, comisiones)

### 4. SISTEMA DE PREMIOS Y RECONOCIMIENTOS
#### Tipos de Premios
- **Premio por Rendimiento**
- **Premio por Antigüedad**
- **Bonificación por Objetivos**
- **Reconocimiento Especial**
- **Incentivo por Productividad**

#### Registro de Premios
- **Fecha de otorgamiento**
- **Tipo de premio**
- **Monto/Valor**
- **Motivo/Descripción**
- **Período evaluado**
- **Usuario que autoriza**

### 5. SISTEMA DISCIPLINARIO
#### Tipos de Sanciones
- **Llamado de atención verbal**
- **Apercibimiento escrito**
- **Suspensión con goce de sueldo**
- **Suspensión sin goce de sueldo**
- **Descuento salarial**

#### Registro de Sanciones
- **Fecha de la sanción**
- **Tipo de sanción**
- **Motivo detallado**
- **Duración (si aplica)**
- **Monto del descuento (si aplica)**
- **Estado** (activa, cumplida, anulada)
- **Usuario que aplica la sanción**
- **Observaciones**

### 6. SISTEMA DE NOTIFICACIONES Y RECORDATORIOS
#### Tipos de Notificaciones
- **Recordatorios Administrativos**
- **Vencimientos de Documentación**
- **Evaluaciones Pendientes**
- **Capacitaciones Obligatorias**
- **Renovación de Contratos**

#### Gestión de Notificaciones
- **Fecha de creación**
- **Fecha de vencimiento**
- **Prioridad** (baja, media, alta, crítica)
- **Estado** (pendiente, vista, completada)
- **Descripción completa**
- **Acciones requeridas**

---

## MEJORAS Y FUNCIONALIDADES ADICIONALES PROPUESTAS

### 7. CONTROL DE ASISTENCIA
- **Registro de horarios de entrada/salida**
- **Control de horas trabajadas**
- **Gestión de ausencias** (licencias, faltas, vacaciones)
- **Cálculo automático de horas extra**
- **Reportes de ausentismo**

### 8. GESTIÓN DOCUMENTAL
- **Archivo digital de documentos:**
  - Contratos firmados
  - Certificados médicos
  - Títulos y certificaciones
  - Evaluaciones de desempeño
  - Constancias varias
- **Control de vencimientos de documentación**
- **Notificaciones automáticas de renovación**

### 9. EVALUACIONES DE DESEMPEÑO
- **Evaluaciones periódicas programables**
- **Criterios de evaluación personalizables**
- **Historial de evaluaciones**
- **Vinculación con aumentos y promociones**
- **Planes de mejora individual**

### 10. CAPACITACIÓN Y DESARROLLO
- **Registro de capacitaciones realizadas**
- **Certificaciones obtenidas**
- **Plan de capacitación anual**
- **Costos de formación**
- **Evaluación de efectividad**

### 11. LIQUIDACIÓN DE SUELDOS
- **Generación automática de recibos**
- **Cálculo de aportes y contribuciones**
- **Integración con sistema contable**
- **Reportes para AFIP/ANSES**
- **Archivo histórico de liquidaciones**

### 12. DASHBOARD Y REPORTES
#### Indicadores Clave (KPIs)
- **Total de empleados por estado**
- **Rotación de personal**
- **Ausentismo promedio**
- **Costo salarial total**
- **Distribución por categorías**
- **Antigüedad promedio**

#### Reportes Automáticos
- **Nómina completa**
- **Vencimientos próximos**
- **Evaluaciones pendientes**
- **Cumpleaños del mes**
- **Aniversarios laborales**
- **Análisis salarial por área**

---

## ESTRUCTURA DE BASE DE DATOS PROPUESTA

### Tabla: empleados
```sql
- id (PK, autoincrement)
- nombre_completo
- dni_cuit
- fecha_nacimiento
- direccion_completa
- telefono_principal
- telefono_secundario
- email_personal
- email_corporativo
- estado_civil
- contacto_emergencia_nombre
- contacto_emergencia_telefono
- fecha_creacion
- fecha_modificacion
- activo (boolean)
```

### Tabla: contratos_laborales
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- fecha_ingreso
- tipo_contrato
- estado_actual
- fecha_finalizacion
- legajo_numero
- observaciones
- fecha_creacion
```

### Tabla: categorias_laborales
```sql
- id (PK, autoincrement)
- nombre_categoria
- departamento
- nivel_jerarquico
- descripcion
- activa (boolean)
```

### Tabla: historial_categorias
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- categoria_anterior_id (FK)
- categoria_nueva_id (FK)
- fecha_cambio
- motivo
- usuario_autoriza
- observaciones
```

### Tabla: historial_salarial
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- salario_anterior
- salario_nuevo
- fecha_cambio
- motivo_ajuste
- porcentaje_aumento
- usuario_autoriza
- observaciones
```

### Tabla: premios_reconocimientos
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- tipo_premio
- monto_valor
- fecha_otorgamiento
- motivo_descripcion
- periodo_evaluado
- usuario_autoriza
- observaciones
```

### Tabla: sanciones_disciplinarias
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- tipo_sancion
- motivo_detallado
- fecha_sancion
- duracion_dias
- monto_descuento
- estado_sancion
- usuario_aplica
- observaciones
- fecha_cumplimiento
```

### Tabla: notificaciones_empleados
```sql
- id (PK, autoincrement)
- empleado_id (FK)
- titulo
- descripcion
- fecha_creacion
- fecha_vencimiento
- prioridad
- estado
- acciones_requeridas
- usuario_crea
```

---

## ASPECTOS DE SEGURIDAD Y AUDITORÍA

### Control de Acceso
- **Roles específicos:** RRHH, Contabilidad, Supervisores, Gerencia
- **Permisos granulares** por funcionalidad
- **Auditoría completa** de todas las operaciones
- **Encriptación** de datos sensibles (salarios, DNI)

### Trazabilidad
- **Registro de todos los cambios** con timestamp
- **Usuario responsable** de cada modificación
- **Historial inmutable** de datos críticos
- **Respaldos automáticos** periódicos

---

## INTEGRACIÓN CON OTROS MÓDULOS

### Módulo de Auditoría
- Registro automático de todas las operaciones RRHH
- Alertas por cambios sensibles (salarios, sanciones)
- Reportes de compliance

### Módulo de Contabilidad
- Cálculo automático de costos laborales
- Integración con liquidación de sueldos
- Proyección de gastos de personal

### Sistema de Notificaciones
- Alertas automáticas por vencimientos
- Notificaciones de cumpleaños/aniversarios
- Recordatorios de evaluaciones

---

## PLAN DE IMPLEMENTACIÓN SUGERIDO

### Fase 1: Estructura Base
1. Crear tablas de base de datos
2. Implementar CRUD básico de empleados
3. Sistema de categorías y cambios

### Fase 2: Gestión Salarial
1. Historial salarial
2. Cálculo de componentes
3. Reportes básicos

### Fase 3: Sistema Disciplinario
1. Premios y reconocimientos
2. Sanciones y suspensiones
3. Notificaciones automáticas

### Fase 4: Funcionalidades Avanzadas
1. Dashboard y KPIs
2. Reportes automáticos
3. Integración completa

### Fase 5: Optimización
1. Performance y escalabilidad
2. Backup y recovery
3. Capacitación usuarios

¿Te parece bien este diseño? ¿Hay alguna funcionalidad específica que quieras que desarrolle primero o algún aspecto que quieras modificar?
