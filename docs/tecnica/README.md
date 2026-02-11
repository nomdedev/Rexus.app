# Documentación Técnica

Esta carpeta contiene documentación técnica detallada sobre arquitectura, configuración y aspectos técnicos del sistema Rexus.app.

## Documentos Disponibles

### Arquitectura y Análisis
- **[ANALISIS_TECNICO_COMPLETO.md](ANALISIS_TECNICO_COMPLETO.md)** - Análisis técnico completo del sistema
- **[TECHNICAL_IMPLEMENTATION_GUIDE.md](TECHNICAL_IMPLEMENTATION_GUIDE.md)** - Guía de implementación técnica

### Configuración
- **[CONFIGURACIONES.md](CONFIGURACIONES.md)** - Configuraciones del sistema
- **[CONFIGURACION_SEGURA.md](CONFIGURACION_SEGURA.md)** - Configuración segura
- **[CONFIGURACION_ANALISIS_CODIGO.md](CONFIGURACION_ANALISIS_CODIGO.md)** - Configuración de análisis de código

## Contenido por Documento

### ANALISIS_TECNICO_COMPLETO.md
Análisis exhaustivo que cubre:
- Estructura de archivos y módulos
- Arquitectura MVC implementada
- Sistema de base de datos SQL Server
- Sistema de seguridad y autenticación
- Componentes de UI (PyQt6)
- Patrones de diseño utilizados
- Integraciones entre módulos

### TECHNICAL_IMPLEMENTATION_GUIDE.md
Guía práctica que incluye:
- Flujo de inicio de la aplicación
- Estructura modular rexus/
- Sistema de login y autenticación
- Conexiones a base de datos
- Sistema de logging
- Gestión de errores
- Deployment

### CONFIGURACIONES.md
Configuraciones del sistema:
- Variables de entorno
- Configuración de desarrollo
- Configuración de producción
- Dependencias principales
- Opciones de compilación

### CONFIGURACION_SEGURA.md
Aspectos de seguridad:
- Configuración de conexiones seguras
- Gestión de secrets
- Políticas de contraseñas
- Certificados SSL/TLS
- Configuración de firewall

### CONFIGURACION_ANALISIS_CODIGO.md
Herramientas de análisis:
- Configuración de linters
- Análisis estático
- Formateo de código
- Type checking
- Análisis de seguridad

## Arquitectura del Sistema

### Estructura de Directorios
```
rexus/
├── core/               # Núcleo del sistema
│   ├── database.py     # Conexión SQL Server
│   ├── security.py     # SecurityManager
│   └── login_dialog.py # Diálogo de login
├── ui/                 # Framework UI
│   ├── dashboard.py    # Dashboard principal
│   └── components/     # Componentes UI
└── utils/              # Utilidades
    ├── app_logger.py   # Logger centralizado
    └── security.py     # Utilidades criptográficas
```

### Stack Tecnológico
- **Framework UI:** PyQt6
- **Base de Datos:** SQL Server con pyodbc
- **Arquitectura:** MVC estricto
- **Testing:** pytest
- **Logging:** Centralizado con niveles
- **Seguridad:** Hash SHA-256 mínimo

## Rutas de Lectura

### Para Nueva Incorporación
1. `ANALISIS_TECNICO_COMPLETO.md` - Visión general
2. `TECHNICAL_IMPLEMENTATION_GUIDE.md` - Detalles de implementación
3. `CONFIGURACIONES.md` - Configuración inicial

### Para Configurar Entorno Seguro
1. `CONFIGURACION_SEGURA.md` - Configuración segura
2. `CONFIGURACION_ANALISIS_CODIGO.md` - Herramientas de análisis
3. Ver también `../auditoria/AUDITORIA_EXPERTA_2025/FASE3_3_AUDITORIA_CONFIGURACION.md`

### Para Entender la Arquitectura
1. `ANALISIS_TECNICO_COMPLETO.md` - Arquitectura completa
2. `../guias/REPOSITORY_SERVICE_PATTERN.md` - Patrones de acceso a datos
3. `../auditoria/AUDITORIA_EXPERTA_2025/FASE2_3_AUDITORIA_ARQUITECTURA.md` - Auditoría de arquitectura

## Diagramas de Arquitectura

### Flujo de Inicio
```
main.py
  setup_environment()
  try: from temp_app import main as app_main
    temp_app.main()
      validate_system_dependencies()
      QApplication(sys.argv)
      SecurityManager()
      LoginDialog()
      MainWindow()
```

### Arquitectura MVC
```
Controller (coordinación)
    ↓
Model (lógica negocio + datos)
    ↓
View (interfaz usuario)
```

### Conexiones a Base de Datos
```
UsersDatabaseConnection
    ↓ (usuarios, permisos)
InventarioConnection
    ↓ (datos de negocio)
AuditoriaConnection
    ↓ (logs, trazabilidad)
```

## Documentos Relacionados

- **[CROSSREFERENCES.md](../CROSSREFERENCES.md)** - Enlaces cruzados entre temas técnicos
- **[README.md](../README.md)** - Documentación principal
- **[CLAUDE.md](../CLAUDE.md)** - Reglas críticas de desarrollo
- **[../guias/README.md](../guias/README.md)** - Guias de implementación

## Temas Técnicos Relacionados

### Base de Datos
- Análisis: `ANALISIS_TECNICO_COMPLETO.md` - Sección Base de Datos
- Auditoría: `../auditoria/AUDITORIA_EXPERTA_2025/FASE1_2_AUDITORIA_BASE_DE_DATOS.md`

### Seguridad
- Configuración: `CONFIGURACION_SEGURA.md`
- Auditoría: `../auditoria/AUDITORIA_EXPERTA_2025/FASE1_1_AUDITORIA_SEGURIDAD.md`

### UI/UX
- Análisis: `ANALISIS_TECNICO_COMPLETO.md` - Sección UI
- Componentes: `TECHNICAL_IMPLEMENTATION_GUIDE.md` - Framework UI
