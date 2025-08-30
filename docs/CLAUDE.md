# 🤖 CLAUDE CONTEXT - Rexus.app v2.0.0 (COMPLETAMENTE REESTRUCTURADO)

**Última actualización:** 30 de Agosto 2025
**Estado:** ✅ ESTRUCTURA COMPLETA Y OPTIMIZADA
**Versión:** 2.0.0 - Production Ready
**Arquitectura:** MVC + SQL Server + PyQt6 + Docker

---

## 🎯 **PARA CUALQUIER IA QUE TRABAJE EN ESTE PROYECTO**

### 🚨 **REGLAS CRÍTICAS ABSOLUTAS (OBLIGATORIO SEGUIR AL 100%)**

#### **1. ESTRUCTURA DE ARCHIVOS - NO MODIFICAR SIN AUTORIZACIÓN**
```
Rexus.app/
├── 📁 .claude/              # Configuración Claude AI
├── 📁 .github/              # Workflows GitHub + dependabot
├── 📁 .vscode/              # Configuración VS Code
├── 📁 AUDITORIA_EXPERTA_2025/  # Documentación auditorías
├── 📁 backups/              # Sistema respaldos automático
├── 📁 cache/                # Cache sistema
├── 📁 config/               # Configuraciones adicionales
├── 📁 docs/                 # 📖 TODA LA DOCUMENTACIÓN AQUÍ
├── 📁 examples/             # Ejemplos de uso
├── 📁 logs/                 # Sistema logging completo
├── 📁 reports/              # Reportes generados
├── 📁 resources/            # Recursos UI (iconos, estilos)
├── 📁 rexus/                # 🏛️ CORE DEL SISTEMA
│   ├── core/               # Base de datos, seguridad, login
│   ├── ui/                 # Framework UI completo
│   └── utils/              # Utilidades centralizadas
├── 📁 scripts/              # Scripts operativos
├── 📁 sql/                  # Scripts SQL centralizados
├── 📁 tests/                # Suite pruebas completa
├── 📄 .env                  # Variables entorno (NO MODIFICAR)
├── 📄 .gitignore            # Control versiones
├── 📄 docker-compose.yml    # Configuración Docker
├── 📄 Dockerfile            # Imagen Docker
├── 📄 main.py               # 🚀 PUNTO ENTRADA PRINCIPAL
├── 📄 Makefile              # Comandos desarrollo
├── 📄 pytest.ini            # Configuración pruebas
└── 📄 requirements.txt      # Dependencias Python
```

#### **2. REGLAS DE IMPORTACIÓN ABSOLUTAS**
```python
# ✅ IMPORTS CORRECTOS (OBLIGATORIOS):
from rexus.core.database import UsersDatabaseConnection
from rexus.core.security import SecurityManager
from rexus.core.login_dialog import LoginDialog
from rexus.core.module_manager import ModuleManager

from rexus.ui.dashboard import DashboardController, DashboardWidget
from rexus.ui.components.theme_manager import ThemeManager
from rexus.ui.components.style_manager import StyleManager

from rexus.utils.app_logger import get_logger, log_info, log_error
from rexus.utils.dependency_validator import validate_system_dependencies
from rexus.utils.security import SecurityUtils
from rexus.utils.sql_query_manager import SQLQueryManager

# 🚫 IMPORTS PROHIBIDOS (ELIMINADOS):
# from temp_app import *          # NO USAR
# from scripts.temp_app import *  # NO USAR
# from legacy_* import *          # ELIMINADOS
# from src.* import *             # ESTRUCTURA ANTIGUA
```

#### **3. ARQUITECTURA MVC ESTRICTA (OBLIGATORIA)**
```python
# 🏗️ MODEL (model.py) - SOLO DATOS Y LÓGICA NEGOCIO:
class ModuloModel:
    def __init__(self):
        self.db = UsersDatabaseConnection()
        self.logger = get_logger(__name__)
        self.sql_manager = SQLQueryManager()

    def get_data(self, filtros=None):
        # ✅ USAR SQL EXTERNO (OBLIGATORIO)
        sql_file = 'sql/modulo/consulta.sql'
        return self.sql_manager.execute_from_file(sql_file, filtros)

# 🎨 VIEW (view.py) - SOLO INTERFAZ USUARIO:
class ModuloView(QWidget):
    modulo_solicitado = pyqtSignal(str)  # ✅ SEÑAL OBLIGATORIA

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()

# 🎯 CONTROLLER (controller.py) - COORDINACIÓN:
class ModuloController:
    def __init__(self):
        self.model = ModuloModel()
        self.view = ModuloView()
        self.connect_view_signals()
```

#### **4. SISTEMA SQL SERVER (OBLIGATORIO)**
```python
# ✅ CONEXIÓN BD (PATRÓN SINGLETON):
from rexus.core.database import UsersDatabaseConnection

db = UsersDatabaseConnection()  # UNA ÚNICA CONEXIÓN

# ✅ SQL EXTERNO (OBLIGATORIO):
# sql/modulo/consulta.sql
SELECT campo1, campo2
FROM tabla
WHERE activo = :activo
ORDER BY fecha_creacion DESC;

# ✅ EJECUCIÓN SQL:
from rexus.utils.sql_query_manager import SQLQueryManager
sql_mgr = SQLQueryManager()
resultado = sql_mgr.execute_from_file('sql/modulo/consulta.sql', {'activo': 1})
```

#### **5. SISTEMA DE LOGGING CENTRALIZADO (OBLIGATORIO)**
```python
# ✅ LOGGING UNIFICADO:
from rexus.utils.app_logger import get_logger, log_info, log_error, log_critical

class MiClase:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    def operacion(self):
        try:
            # Operación
            log_info("Operación exitosa", "mi_modulo")
            return True
        except Exception as e:
            log_error(f"Error: {str(e)}", "mi_modulo")
            return False
```

#### **6. GESTIÓN DE ERRORES Y EXCEPTIONS (OBLIGATORIA)**
```python
# ✅ PATRÓN DE MANEJO ERRORES:
def operacion_critica(self):
    try:
        resultado = self.model.operacion()
        return resultado
    except ConnectionError:
        log_error("Error de conexión BD", "database")
        self.view.show_error("Error de conexión")
    except ValueError as e:
        log_error(f"Datos inválidos: {e}", "validation")
        self.view.show_error("Datos incorrectos")
    except Exception as e:
        log_critical(f"Error crítico: {e}", "system")
        self.view.show_error("Error interno del sistema")
```

#### **7. VALIDACIONES DE SEGURIDAD (OBLIGATORIAS)**
```python
# ✅ VALIDACIONES SECURITY:
from rexus.utils.security import SecurityUtils

def validar_usuario(self, username, password):
    # Hash obligatorio
    password_hash = SecurityUtils.hash_password(password)

    # Validar contra BD
    user_data = self.db.validate_credentials(username, password_hash)

    # Log de auditoría obligatorio
    log_info(f"Login attempt: {username}", "security")

    return user_data
```

#### **8. UI/UX - COMPONENTES ESTÁNDAR (OBLIGATORIOS)**
```python
# ✅ COMPONENTES STANDARD:
from rexus.ui.components.theme_manager import ThemeManager
from rexus.ui.components.style_manager import StyleManager

class MiVista(QWidget):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.style_manager = StyleManager()
        self.setup_ui()

    def setup_ui(self):
        # Aplicar tema obligatorio
        self.setStyleSheet(self.theme_manager.get_current_theme())

        # Componentes standard
        self.table = self.create_data_table()
        self.search = self.create_search_box()
        self.buttons = self.create_action_buttons()
```

---

## 🏗️ **ARQUITECTURA TÉCNICA COMPLETA**

### **📊 FLUJO DE INICIO DE LA APLICACIÓN**

```
1. 🚀 main.py
   └── setup_environment()
   └── try: from temp_app import main as app_main
       └── ✅ temp_app.main()
       └── ❌ run_basic_mode()
           └── ❌ run_emergency_mode()

2. 📋 temp_app.main()
   └── validate_system_dependencies()
   └── QApplication(sys.argv)
   └── SecurityManager()
   └── LoginDialog()
   └── MainWindow()
   └── app.exec()
```

### **🏛️ ESTRUCTURA MODULAR rexus/**

#### **📁 rexus/core/ - NÚCLEO DEL SISTEMA**
- **`database.py`** - Conexión SQL Server (Singleton)
- **`security.py`** - SecurityManager y autenticación
- **`login_dialog.py`** - Diálogo login con validaciones
- **`module_manager.py`** - Gestión módulos dinámicos

#### **📁 rexus/ui/ - FRAMEWORK UI**
- **`dashboard.py`** - Dashboard principal con señales
- **`components/`** - Tema, estilos, componentes estándar
- **`executive_dashboard.py`** - Dashboard ejecutivo

#### **📁 rexus/utils/ - UTILIDADES CENTRALIZADAS**
- **`app_logger.py`** - Logger centralizado (Singleton)
- **`dependency_validator.py`** - Validación dependencias
- **`security.py`** - Utilidades criptográficas
- **`sql_query_manager.py`** - Gestor consultas SQL

---

## 🔒 **SISTEMA DE SEGURIDAD (CRÍTICO)**

### **🚨 REGLAS ABSOLUTAS DE SEGURIDAD:**

#### **1. AUTENTICACIÓN CON TABLAS REALES (OBLIGATORIO)**
```python
# ✅ USAR SOLO ESTAS TABLAS PARA AUTENTICACIÓN:
# - Tabla: usuarios (BD users)
# - Tabla: permisos_usuario (BD users)

# ✅ SQL EXTERNO OBLIGATORIO:
user_result = sql_manager.ejecutar_consulta_archivo(
    'sql/09_usuarios/autenticar_usuario.sql',
    (username,)
)

# ✅ VERIFICACIÓN MULTI-ALGORITMO:
# - bcrypt (preferido)
# - SHA-256 (legacy)
# - MD5 (deprecado)
# - Texto plano (SOLO para migración)
```

#### **2. CONTRASEÑAS - PROHIBICIONES ABSOLUTAS:**
```python
# 🚫 JAMÁS HACER:
password = "contraseña_hardcodeada"  # PROHIBIDO
REXUS_DEV_PASSWORD = "password"      # PROHIBIDO
user_password = "123456"             # PROHIBIDO

# ✅ OBLIGATORIO:
# - Obtener contraseñas SOLO de base de datos
# - Usar hash bcrypt para nuevas contraseñas
# - Soportar múltiples algoritmos para migración
# - Log de seguridad en todos los intentos
```

#### **3. SISTEMA DE PERMISOS POR MÓDULO (OBLIGATORIO)**
```python
# ✅ PERMISOS POR ROL (FALLBACK):
ROLE_PERMISSIONS = {
    'ADMINISTRADOR': ['usuarios', 'inventario', 'pedidos', 'compras', 
                      'vidrios', 'herrajes', 'obras', 'logistica', 
                      'mantenimiento', 'configuracion', 'auditoria'],
    'SUPERVISOR': ['inventario', 'pedidos', 'compras', 'vidrios', 
                   'herrajes', 'obras', 'logistica', 'mantenimiento'],
    'VENDEDOR': ['pedidos', 'vidrios', 'herrajes', 'inventario'],
    'USUARIO': ['inventario', 'pedidos', 'vidrios']
}

# ✅ VERIFICACIÓN DE PERMISOS:
def verificar_permiso_modulo(usuario_id: int, modulo: str) -> bool:
    # 1. Buscar en tabla permisos_usuario
    # 2. Fallback a permisos por rol
    # 3. Denegar por defecto
```

#### **4. AUDITORÍA DE SEGURIDAD (OBLIGATORIA)**
```python
# ✅ LOG OBLIGATORIO EN TODOS LOS EVENTOS:
log_security("LOGIN_ATTEMPT", f"Usuario {username} intenta login", username)
log_security("LOGIN_SUCCESS", f"Usuario {username} autenticado", username) 
log_security("LOGIN_FAILED", f"Login fallido para {username}", username)
log_security("ACCESS_DENIED", f"Acceso denegado a {modulo}", username)
log_security("PASSWORD_PLAIN", f"Usuario {username} usa contraseña texto plano", "system")
```

#### **5. VALIDACIONES SQL INJECTION (CRÍTICO)**
```python
# ✅ OBLIGATORIO - SQL PARAMETRIZADO:
cursor.execute("SELECT * FROM tabla WHERE id = ?", (user_id,))

# 🚫 PROHIBIDO - SQL DINÁMICO:
cursor.execute(f"SELECT * FROM tabla WHERE id = {user_id}")
cursor.execute("SELECT * FROM tabla WHERE nombre = '" + nombre + "'")
query = f"UPDATE {tabla} SET campo = '{valor}'"  # NUNCA
```

### **CAPAS DE SEGURIDAD IMPLEMENTADAS:**
1. **Autenticación**: Tablas usuarios reales + hash multi-algoritmo
2. **Autorización**: Permisos por tabla + fallback por rol
3. **Validación**: SQL parametrizado + validación de entrada
4. **Auditoría**: Log completo de eventos de seguridad
5. **Encriptación**: AES para datos sensibles + bcrypt para contraseñas

### **CONFIGURACIÓN SEGURIDAD (.env):**
```env
# Claves de encriptación
SECRET_KEY=rexus_secret_key_production_2025_...
JWT_SECRET_KEY=jwt_rexus_2025_...
ENCRYPTION_KEY=encryption_rexus_2025_...

# Base de datos (NO CONTRASEÑAS DE USUARIO)
DB_SERVER=servidor
DB_USERNAME=usuario_bd
DB_PASSWORD=password_bd
DB_USERS=users
```

---

## 🐳 **CONFIGURACIÓN DOCKER**

### **Dockerfile (OBLIGATORIO):**
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get install -y build-essential libgl1 libegl1...
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### **docker-compose.yml:**
```yaml
version: '3.8'
services:
  rexus:
    build: .
    volumes: [".:/app"]
    environment:
      - PYTHONUNBUFFERED=1
    command: ["python", "main.py"]
```

---

## 🧪 **SISTEMA DE PRUEBAS**

### **pytest.ini (OBLIGATORIO):**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --tb=short --cov=rexus
```

### **ESTRUCTURA TESTS:**
```
tests/
├── unit/          # Pruebas unitarias
├── integration/   # Pruebas integración
├── ui/           # Pruebas interfaz
├── e2e/          # Pruebas end-to-end
└── conftest.py   # Configuración
```

---

## 📊 **SISTEMA DE LOGGING**

### **ARCHIVOS LOG GENERADOS:**
```
logs/
├── rexus.log              # Principal
├── authentication.log     # Autenticación
├── database.log           # Base datos
├── security.log           # Seguridad
├── ui.log                 # Interfaz
├── cache.log              # Cache
└── backup_system.log      # Respaldos
```

### **NIVELES LOGGING:**
- **DEBUG**: Desarrollo detallado
- **INFO**: Información general
- **WARNING**: Advertencias
- **ERROR**: Errores no críticos
- **CRITICAL**: Errores críticos

---

## 🔄 **SISTEMA DE CACHÉ Y RESPALDOS**

### **CONFIGURACIÓN CACHÉ:**
```env
CACHE_TYPE=memory
CACHE_DEFAULT_TIMEOUT=3600
```

### **CONFIGURACIÓN RESPALDOS:**
```env
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
```

---

## 🎯 **MODOS DE EJECUCIÓN**

### **DESARROLLO:**
```bash
python main.py --dev
# o
REXUS_ENV=development python main.py
```

### **PRODUCCIÓN:**
```bash
python main.py
```

### **DOCKER:**
```bash
make dev-docker
# o
docker-compose up --build
```

---

## 📋 **DEPENDENCIAS PRINCIPALES**

### **CORE:**
- **PyQt6**: Framework UI
- **pyodbc**: SQL Server
- **python-dotenv**: Variables entorno

### **SEGURIDAD:**
- **cryptography**: Encriptación
- **bcrypt**: Hash passwords
- **argon2-cffi**: Hash moderno

### **UTILIDADES:**
- **pandas**: Procesamiento datos
- **requests**: APIs
- **Pillow**: Imágenes

### **DESARROLLO:**
- **pytest**: Tests
- **black**: Formateo
- **flake8**: Linting

---

## 🚀 **COMANDOS DESARROLLO (Makefile)**

```bash
make dev         # Desarrollo local
make dev-docker  # Desarrollo Docker
make build       # Build imagen
make install     # Instalar dependencias
make clean       # Limpiar containers
make help        # Ayuda
```

---

## 🔧 **MANEJO ERRORES Y FALLBACKS**

### **SISTEMA FALLBACKS:**
1. **Error Import**: temp_app → basic_mode → emergency_mode
2. **Error BD**: Conexión real → modo sin BD
3. **Error Security**: Autenticación real → usuario guest
4. **Error UI**: Componentes completos → componentes básicos

---

## 📊 **MÉTRICAS Y MONITOREO**

### **MÉTRICAS SISTEMA:**
- Tiempo respuesta queries
- Uso memoria
- Conexiones BD activas
- Usuarios concurrentes
- Operaciones por módulo

---

## 🎯 **REGLAS ESPECÍFICAS DESARROLLO**

### **1. SQL EXTERNO OBLIGATORIO:**
```sql
-- ✅ sql/modulo/consulta.sql
SELECT campo1, campo2
FROM tabla
WHERE activo = :activo;
```

### **2. LOGGING EN TODAS OPERACIONES:**
```python
# ✅ OBLIGATORIO en cada método
self.logger.info("Operación iniciada")
try:
    # operación
    self.logger.info("Operación exitosa")
except Exception as e:
    self.logger.error(f"Error: {e}")
```

### **3. VALIDACIONES SECURITY:**
```python
# ✅ OBLIGATORIO en forms
def validate_input(self, data):
    if not SecurityUtils.validate_email(data.get('email')):
        raise ValueError("Email inválido")
```

### **4. TESTING OBLIGATORIO:**
```python
# ✅ Tests para cada nueva funcionalidad
def test_mi_funcionalidad():
    # Arrange
    # Act
    # Assert
```

### **5. DOCUMENTACIÓN OBLIGATORIA:**
```python
def mi_funcion(param1: str, param2: int) -> dict:
    """
    Descripción completa de qué hace la función.

    Args:
        param1: Descripción parámetro 1
        param2: Descripción parámetro 2

    Returns:
        Descripción retorno

    Raises:
        ExceptionType: Cuando ocurre esto
    """
```

---

## 📝 **MANTENIMIENTO CLAUDE.MD**

### **🔄 REGLA FUNDAMENTAL:**
**ESTE ARCHIVO DEBE MANTENERSE SIEMPRE ACTUALIZADO**

### **ACTUALIZACIONES OBLIGATORIAS:**
1. **Cambios arquitectura** → Actualizar estructura
2. **Nuevas reglas** → Agregar inmediatamente
3. **Nuevos patrones** → Documentar
4. **Cambios dependencias** → Actualizar lista
5. **Nuevos comandos** → Agregar a Makefile/docs

### **📅 HISTORIAL ACTUALIZACIONES:**
- **30 Ago 2025**: Reestructuración completa + reglas SQL Server
- **17 Ago 2025**: Documentación inicial post-reestructuración

---

## 🚨 **NOTAS CRÍTICAS PARA DESARROLLO**

### **❌ PROHIBIDO:**
- Modificar `.env` sin autorización
- Crear archivos en raíz (solo fundamentales)
- Usar queries SQL hardcodeadas
- Imports desde rutas eliminadas
- Modificar estructura sin actualizar este archivo

### **✅ OBLIGATORIO:**
- Usar SQL externo para todas queries
- Logging en todas operaciones críticas
- Validaciones security en inputs
- Tests para nuevas funcionalidades
- Actualizar este archivo con cambios

### **🔧 MEJORES PRÁCTICAS:**
- Commit temprano y frecuente
- Code review obligatorio
- Documentación inline completa
- Manejo errores comprehensivo
- Performance monitoring

---

## 📞 **CONTACTO Y SOPORTE**

**Para soporte técnico:**
- Revisar `docs/ANALISIS_TECNICO_COMPLETO.md`
- Verificar logs en `logs/`
- Consultar `docs/` para documentación específica

**Para desarrollo:**
- Seguir reglas de este archivo
- Usar comandos del Makefile
- Mantener estructura de archivos
- Actualizar documentación

---

*Fin del documento - Última actualización: 30 de Agosto 2025*

class ModuloModel:
    def __init__(self):
        self.sql_manager = SQLQueryManager()
    
    def obtener_datos(self, filtros=None):
        # Usar archivo SQL externo
        sql_file = 'sql/modulo/consulta_datos.sql'
        return self.sql_manager.ejecutar_consulta_archivo(sql_file, filtros)

# 🚫 NUNCA HACER:
# - Queries hardcodeadas en strings
# - Concatenación de strings SQL
# - Acceso directo a BD desde views
```

##### **C. Scripts SQL Externos:**
```sql
-- sql/modulo/consulta_datos.sql
-- ✅ ESTRUCTURA OBLIGATORIA:
SELECT 
    campo1,
    campo2,
    campo3
FROM tabla_principal t1
LEFT JOIN tabla_relacionada t2 ON t1.id = t2.tabla_id
WHERE t1.activo = :activo
  AND (:filtro IS NULL OR t1.nombre LIKE :filtro)
ORDER BY t1.fecha_creacion DESC;
```

##### **D. Manejo de Errores y Logging:**
```python
# ✅ PATRÓN OBLIGATORIO:
from rexus.utils.app_logger import get_logger

class ModuloController:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def operacion_critica(self):
        try:
            # Operación principal
            resultado = self.model.operacion()
            self.logger.info(f"Operación exitosa: {resultado}")
            return resultado
        except Exception as e:
            self.logger.error(f"Error en operación: {str(e)}")
            self.view.mostrar_error("Error procesando solicitud")
            return None
```

##### **E. UI/UX Componentes:**
```python
# ✅ USAR COMPONENTES ESTÁNDAR:
from rexus.ui.standard_components import StandardComponents
from rexus.ui.base_module_view import BaseModuleView

class ModuloView(BaseModuleView):
    def setup_ui(self):
        # Componentes estándar
        self.table = StandardComponents.create_table()
        self.search_box = StandardComponents.create_search_box()
        self.buttons = StandardComponents.create_button_panel()
        
        # ✅ Aplicar tema automáticamente
        self.apply_theme()
```

---

## 📊 ESTADO ACTUAL DEL PROYECTO

### ✅ COMPLETADO (100%):
- **Reestructuración completa** - Eliminados duplicados y legacy
- **Imports unificados** - Todos corregidos a nueva estructura  
- **SQL externos** - Herrajes y Vidrios completamente migrados
- **Cache Manager** - Consolidado en utils con get_cache_manager()
- **Security Utils** - Unificado con aliases de compatibilidad
- **UI/UX Framework** - BaseModuleView y StandardComponents funcionando

### 🔄 EN PROGRESO:
- **Migración SQL** - Usuarios, Inventario, Obras, Pedidos, Compras pendientes
- **Testing completo** - Validación post-reestructuración

### 📋 MÓDULOS ESTADO:
```
✅ Herrajes      - 100% modernizado (SQL externo + UI/UX completa)
✅ Vidrios       - 100% modernizado (SQL externo + UI/UX completa)  
✅ Compras       - 90% funcional (UI/UX completa, SQL parcial)
✅ Pedidos       - 90% funcional (UI/UX completa, SQL parcial)
🔄 Usuarios      - 80% funcional (SQL hardcodeado pendiente)
🔄 Inventario    - 80% funcional (SQL hardcodeado pendiente)
🔄 Obras         - 80% funcional (SQL hardcodeado pendiente)
✅ Auditoría     - 100% funcional
✅ Configuración - 100% funcional
✅ Logística     - 100% funcional
✅ Mantenimiento - 100% funcional
```

---

## 🛠️ COMANDOS DE DESARROLLO (OBLIGATORIO USAR ESTOS)

### **1. Ejecutar la Aplicación:**
```bash
# Punto de entrada principal
python main.py

# Modo desarrollo con auto-login
python main.py --dev
# O con variables de entorno:
# REXUS_ENV=development
# HOTRELOAD_ENABLED=true
# REXUS_DEV_AUTO_LOGIN=true

# Desarrollo con Docker
make dev-docker
docker-compose up --build

# Desarrollo local con Make
make dev        # Inicia servidor de desarrollo
make install    # Instala dependencias
make clean      # Limpia containers Docker
```

### **2. Testing Completo (OBLIGATORIO):**
```bash
# Suite completa de tests con pytest
python -m pytest tests/ -v --tb=short --disable-warnings

# Tests por categorías (definidas en pytest.ini)
python -m pytest -m unit         # Tests unitarios
python -m pytest -m integration  # Tests de integración  
python -m pytest -m ui          # Tests de interfaz
python -m pytest -m security    # Tests de seguridad
python -m pytest -m performance # Tests de rendimiento
python -m pytest -m e2e         # Tests end-to-end

# Test específico de un módulo
python -m pytest tests/test_{modulo}.py -v

# Tests con cobertura
python -m pytest tests/ --cov=rexus --cov-report=html
```

### **3. Auditoría de Seguridad (OBLIGATORIO):**
```bash
# Auditoría completa del sistema
python tools/comprehensive_audit.py

# Validación de calidad de código
python scripts/tools/fix_code_quality.py

# Verificación de correcciones
python scripts/tools/verify_fixes.py

# Análisis de vulnerabilidades con Bandit
bandit -r rexus/ -f json -o reports/bandit_scan.json
```

### **4. Validación de Estructura Post-Reestructuración:**
```bash
# Validar imports principales
python -c "import rexus; print('✅ Core OK')"
python -c "from rexus.utils.app_logger import get_logger; print('✅ Logger OK')"  
python -c "from rexus.utils.sql_query_manager import SQLQueryManager; print('✅ SQL Manager OK')"
python -c "from rexus.core.database import get_inventario_connection; print('✅ Database OK')"

# Contar archivos en estructura final
Get-ChildItem -Path "rexus" -Name "*.py" -Recurse | Measure-Object
```

### **5. Antes de Crear Cualquier Archivo:**
```bash
# ¿Existe ya este archivo?
find . -name "*nombre_archivo*" -type f

# ¿Hay duplicados del mismo tipo?
Get-ChildItem -Path . -Name "*.py" -Recurse | Where-Object { $_ -notlike "*.venv*" } | Group-Object { ($_ -split '\\')[-1] } | Where-Object { $_.Count -gt 1 }

# ¿Dónde debe ir según las convenciones?
# - Utilidades: rexus/utils/
# - Módulos: rexus/modules/{modulo}/
# - SQL: sql/{modulo}/
# - Tests: tests/
```

### **6. Validar Módulo Después de Cambios:**
```python
# Template de validación
python -c "
try:
    from rexus.modules.{MODULO}.model import {MODULO}Model
    from rexus.modules.{MODULO}.view import {MODULO}View  
    from rexus.modules.{MODULO}.controller import {MODULO}Controller
    print('✅ {MODULO} - Todos los archivos OK')
except Exception as e:
    print(f'❌ {MODULO} - Error: {e}')
"
```

### **7. Migrar SQL a Archivos Externos:**
```python
# Script para extraer queries hardcodeadas
python tools/migrate_sql_to_files.py --module {MODULO}

# Verificar que no quedan queries hardcodeadas
grep -r "SELECT\|INSERT\|UPDATE\|DELETE" rexus/modules/{MODULO}/ --include="*.py" | grep -v "sql_manager"
```

---

## 🎯 REGLAS DE DESARROLLO ESPECÍFICAS

### **🗃️ SQL Server - Gestión Obligatoria:**
```python
# ✅ OBLIGATORIO: SQL en archivos externos bajo sql/
sql_manager = SQLQueryManager()
resultado = sql_manager.ejecutar_consulta_archivo(
    'sql/modulo/operacion_especifica.sql', 
    parametros={'id': valor_id, 'estado': 'activo'}
)

# 🚫 PROHIBIDO COMPLETAMENTE: Queries embebidos o concatenados
query = f"SELECT * FROM tabla WHERE id = {id}"  # ❌ NUNCA HACER
query = "SELECT * FROM tabla WHERE campo = '" + valor + "'"  # ❌ NUNCA HACER
```

### **✅ Validación de Variables - SIEMPRE OBLIGATORIO:**
```python
# ✅ PATRÓN OBLIGATORIO: Validar TODO antes de procesar
def procesar_datos(self, datos):
    # 1. Validación de existencia
    if not datos:
        self.logger.error("Datos no proporcionados")
        self.view.mostrar_error("Datos requeridos")
        return None
    
    # 2. Validación de tipos
    if not isinstance(datos.get('id'), (int, str)) or not datos.get('id'):
        self.logger.error(f"ID inválido: {datos.get('id')}")
        self.view.mostrar_error("ID inválido")
        return None
    
    # 3. Validación de campos requeridos
    campos_requeridos = ['nombre', 'tipo', 'estado']
    for campo in campos_requeridos:
        if not datos.get(campo):
            self.logger.error(f"Campo requerido faltante: {campo}")
            self.view.mostrar_error(f"El campo {campo} es requerido")
            return None
    
    # Solo proceder si TODO está validado
    return self._ejecutar_operacion_segura(datos)
```

### **🎨 Formularios - Estilo Visual Uniforme OBLIGATORIO:**
```python
# ✅ TEMPLATE OBLIGATORIO para cualquier formulario/vista:
from rexus.ui.base_module_view import BaseModuleView
from rexus.ui.standard_components import StandardComponents

class ModuloView(BaseModuleView):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_theme()  # ✅ OBLIGATORIO - Nunca omitir
    
    def setup_ui(self):
        # Panel de búsqueda estándar
        self.search_panel = StandardComponents.create_search_panel([
            ('buscar', 'text', 'Buscar...'),
            ('categoria', 'combo', self.get_categorias()),
            ('estado', 'combo', ['Activo', 'Inactivo', 'Todos'])
        ])
        
        # Tabla principal con configuración estándar
        self.main_table = StandardComponents.create_table(
            columns=self.get_columns(),
            enable_sorting=True,
            enable_filtering=True,
            enable_export=True,
            row_height=35
        )
        
        # Panel de estadísticas uniforme
        self.stats_panel = StandardComponents.create_stats_panel([
            ('Total', self.get_total_count),
            ('Activos', self.get_active_count),  
            ('Inactivos', self.get_inactive_count)
        ])
        
        # Botones de acción estándar
        self.action_buttons = StandardComponents.create_button_panel([
            ('Nuevo', 'primary', self.nuevo_registro),
            ('Editar', 'secondary', self.editar_registro),
            ('Eliminar', 'danger', self.eliminar_registro),
            ('Exportar', 'info', self.exportar_datos)
        ])
        
        # Layout uniforme
        self.setup_standard_layout()
```

### **🔗 Interacción BD - Patrón Completo MVC:**
```python
# ✅ CONTROLLER - Coordinación completa
class ModuloController:
    def __init__(self):
        self.model = ModuloModel()
        self.view = ModuloView()
        self.logger = get_logger(self.__class__.__name__)
        self.setup_connections()
    
    def setup_connections(self):
        # Conectar señales de vista con métodos de controller
        self.view.nuevo_clicked.connect(self.crear_registro)
        self.view.editar_clicked.connect(self.editar_registro)
        self.view.eliminar_clicked.connect(self.eliminar_registro)
        self.view.buscar_changed.connect(self.buscar_registros)
    
    def crear_registro(self, datos):
        try:
            # 1. Validar datos completos
            datos_validados = self._validar_datos_completos(datos)
            if not datos_validados:
                return False
            
            # 2. Procesar en model
            resultado = self.model.crear_registro(datos_validados)
            
            # 3. Actualizar vista según resultado
            if resultado:
                self.logger.info(f"Registro creado: {resultado}")
                self.view.mostrar_exito("Registro creado exitosamente")
                self.view.actualizar_tabla()
                self.view.limpiar_formulario()
            else:
                self.logger.warning("Fallo al crear registro")
                self.view.mostrar_advertencia("No se pudo crear el registro")
                
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error creando registro: {str(e)}")
            self.view.mostrar_error("Error interno al crear registro")
            return False

# ✅ MODEL - Solo lógica de negocio y datos
class ModuloModel:
    def __init__(self):
        self.sql_manager = SQLQueryManager(get_inventario_connection())
        self.logger = get_logger(self.__class__.__name__)
    
    def crear_registro(self, datos):
        try:
            # Usar archivo SQL externo
            resultado = self.sql_manager.ejecutar_consulta_archivo(
                'sql/modulo/crear_registro.sql',
                parametros=datos
            )
            
            if resultado:
                # Registrar auditoría
                self._registrar_auditoria('CREATE', datos)
                return resultado.get('id') or True
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error en model crear_registro: {str(e)}")
            raise
```

### **🧪 Testing OBLIGATORIO - Para Cada Módulo:**
```python
# tests/test_modulo_completo.py
import pytest
from unittest.mock import Mock, patch
from rexus.modules.modulo.controller import ModuloController
from rexus.modules.modulo.model import ModuloModel
from rexus.modules.modulo.view import ModuloView

class TestModuloCompleto:
    """Suite completa de tests para módulo"""
    
    @pytest.fixture
    def controller(self):
        return ModuloController()
    
    @pytest.fixture
    def datos_validos(self):
        return {
            'nombre': 'Test Item',
            'tipo': 'TIPO_A', 
            'estado': 'activo',
            'descripcion': 'Item de prueba'
        }
    
    # ✅ Test de creación exitosa
    def test_crear_registro_datos_validos(self, controller, datos_validos):
        resultado = controller.crear_registro(datos_validos)
        assert resultado is not False
        assert controller.view.mensaje_exito_mostrado
    
    # ✅ Test de validación de datos
    def test_validacion_datos_invalidos(self, controller):
        datos_invalidos = {'nombre': None, 'tipo': ''}
        resultado = controller.crear_registro(datos_invalidos)
        assert resultado is False
        assert controller.view.mensaje_error_mostrado
    
    # ✅ Test de interacción con BD
    def test_model_ejecuta_sql_correcto(self, datos_validos):
        model = ModuloModel()
        with patch.object(model.sql_manager, 'ejecutar_consulta_archivo') as mock_sql:
            mock_sql.return_value = {'id': 123}
            
            resultado = model.crear_registro(datos_validos)
            
            mock_sql.assert_called_once_with(
                'sql/modulo/crear_registro.sql',
                parametros=datos_validos
            )
            assert resultado == 123
    
    # ✅ Test de UI/UX
    def test_interfaz_componentes_estandar(self):
        view = ModuloView()
        assert hasattr(view, 'main_table')
        assert hasattr(view, 'search_panel')
        assert hasattr(view, 'action_buttons')
        assert hasattr(view, 'apply_theme')
    
    # ✅ Test de seguridad
    def test_sql_injection_protection(self, controller):
        datos_maliciosos = {
            'nombre': "'; DROP TABLE usuarios; --",
            'tipo': 'TIPO_A'
        }
        # No debe fallar ni ejecutar SQL malicioso
        resultado = controller.crear_registro(datos_maliciosos)
        # Debe ser validado y rechazado o escapado correctamente
        assert resultado is not None  # El sistema debe manejar esto
```

---

## 🎨 ESTÁNDARES UI/UX MODERNOS

### **Componentes Obligatorios:**
```python
# ✅ Template base para cualquier módulo:
from rexus.ui.base_module_view import BaseModuleView
from rexus.ui.standard_components import StandardComponents

class ModuloView(BaseModuleView):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_theme()  # ✅ OBLIGATORIO
    
    def setup_ui(self):
        # Panel de control estándar
        self.control_panel = StandardComponents.create_control_panel()
        
        # Tabla principal con estilos
        self.main_table = StandardComponents.create_table(
            columns=self.get_columns(),
            enable_sorting=True,
            enable_filtering=True
        )
        
        # Panel de estadísticas
        self.stats_panel = StandardComponents.create_stats_panel()
        
        # Botones de acción estándar
        self.action_buttons = StandardComponents.create_button_panel([
            ('Nuevo', 'primary'),
            ('Editar', 'secondary'), 
            ('Eliminar', 'danger'),
            ('Exportar', 'info')
        ])
```

### **Temas y Colores:**
```python
# ✅ Usar constantes de color estándar:
from rexus.ui.colors import RexusColors

# Colores disponibles:
RexusColors.PRIMARY       # Color principal del tema
RexusColors.SECONDARY     # Color secundario
RexusColors.SUCCESS       # Verde para éxito
RexusColors.WARNING       # Amarillo para advertencias  
RexusColors.DANGER        # Rojo para errores
RexusColors.INFO          # Azul para información
RexusColors.TEXT_PRIMARY  # Texto principal
RexusColors.TEXT_SECONDARY # Texto secundario
RexusColors.BACKGROUND    # Fondo principal
```

---

## 🗃️ BASE DE DATOS - ARQUITECTURA FINAL

### **Conexiones Disponibles:**
```python
# ✅ USAR ESTAS CONEXIONES ESPECÍFICAS:
from rexus.core.database import (
    get_inventario_connection,  # DATOS DE NEGOCIO
    get_users_connection,       # SOLO USUARIOS Y PERMISOS  
    get_auditoria_connection    # SOLO LOGS Y AUDITORÍA
)

# 🎯 REGLA CRÍTICA - SEPARACIÓN DE DATOS:
# - users DB: Solo login, permisos, roles
# - inventario DB: Todos los datos de negocio (productos, obras, pedidos, etc.)
# - auditoria DB: Solo logs, trazabilidad, eventos de seguridad
```

### **SQL Query Manager Unificado:**
```python
# ✅ PATRÓN ESTÁNDAR PARA TODAS LAS CONSULTAS:
from rexus.utils.sql_query_manager import SQLQueryManager

class ModuloModel:
    def __init__(self):
        self.sql_manager = SQLQueryManager(get_inventario_connection())
    
    def obtener_registros(self, filtros=None):
        # Archivo SQL externo
        return self.sql_manager.ejecutar_consulta_archivo(
            'sql/modulo/obtener_registros.sql',
            parametros=filtros or {}
        )
    
    def crear_registro(self, datos):
        # Usar consulta preparada
        return self.sql_manager.ejecutar_consulta_archivo(
            'sql/modulo/crear_registro.sql',
            parametros=datos
        )
```

---

## 📁 ORGANIZACIÓN DE ARCHIVOS SQL

### **Estructura Obligatoria:**
```
sql/
├── common/                    # Consultas compartidas
│   ├── verificar_tabla.sql
│   ├── backup_datos.sql
│   └── sistema_salud.sql
├── usuarios/                  # 🔄 PENDIENTE MIGRAR
├── inventario/               # 🔄 PENDIENTE MIGRAR  
├── obras/                    # 🔄 PENDIENTE MIGRAR
├── pedidos/                  # 🔄 PENDIENTE MIGRAR
├── compras/                  # 🔄 PENDIENTE MIGRAR
├── herrajes/                 # ✅ COMPLETADO
│   ├── obtener_herrajes.sql
│   ├── buscar_herrajes.sql
│   ├── crear_herraje.sql
│   └── eliminar_herraje.sql
└── vidrios/                  # ✅ COMPLETADO
    ├── obtener_vidrios.sql
    ├── buscar_vidrios.sql
    └── crear_vidrio.sql
```

### **Template SQL Estándar:**
```sql
-- sql/{modulo}/consulta_ejemplo.sql
-- Descripción: Breve descripción de la consulta
-- Parámetros: :param1, :param2, :param3
-- Retorna: Estructura de datos esperada

SELECT 
    t1.id,
    t1.nombre,
    t1.descripcion,
    t1.fecha_creacion,
    t2.categoria_nombre
FROM {tabla_principal} t1
LEFT JOIN categorias t2 ON t1.categoria_id = t2.id  
WHERE t1.activo = :activo
  AND (:filtro_nombre IS NULL OR t1.nombre LIKE :filtro_nombre)
  AND (:categoria_id IS NULL OR t1.categoria_id = :categoria_id)
ORDER BY t1.fecha_creacion DESC
LIMIT :limite OFFSET :offset;
```

---

## 🔧 HERRAMIENTAS DISPONIBLES

### **Tools Únicos (NO DUPLICAR):**
```
tools/
├── comprehensive_audit.py          # Auditoría completa del sistema
├── deploy_production.py            # Deploy a producción
├── migrate_controllers_to_base.py  # Migración a BaseModuleView  
├── migrate_prints_dryrun.py        # Vista previa migración logging
├── migrate_prints_to_logging.py    # Migración completa logging
└── migrate_sql_to_files.py         # Migración SQL a archivos

scripts/tools/                      # Scripts operativos completos
├── aplicar_estilos_premium.py      # Aplicar temas premium
├── cleanup_duplicates.py           # Limpieza de duplicados
├── expert_audit.py                 # Auditoría experta
├── fix_code_quality.py             # Corrección calidad código
└── verify_fixes.py                 # Verificación de fixes
```

### **Testing Automático:**
```bash
# Suite completa de tests
python -m pytest tests/ -v

# Tests específicos por módulo  
python -m pytest tests/test_{modulo}.py -v

# Tests de UI/UX
python tests/ui/ui_validation_simple.py

# Auditoría de seguridad
python tools/comprehensive_audit.py
```

---

## 🚨 PROBLEMAS CONOCIDOS Y SOLUCIONES

### **1. Imports Legacy (ELIMINADOS):**
```python
# 🚫 SI VES ESTOS IMPORTS, CORREGIR INMEDIATAMENTE:
from legacy_root.*
from src.*
from utils.* (nivel raíz)

# ✅ CORREGIR A:
from rexus.utils.*
from rexus.core.*
from rexus.modules.*
```

### **2. SQL Hardcodeado (EN MIGRACIÓN):**
```python
# 🚫 ELIMINAR QUERIES HARDCODEADAS:
query = "SELECT * FROM tabla WHERE campo = '" + valor + "'"

# ✅ USAR ARCHIVOS SQL:
resultado = self.sql_manager.ejecutar_consulta_archivo(
    'sql/modulo/consulta.sql', 
    {'campo': valor}
)
```

### **3. UI sin Temas (CORREGIR):**
```python
# 🚫 WIDGETS SIN TEMA:
button = QPushButton("Texto")

# ✅ USAR COMPONENTES ESTÁNDAR:
button = StandardComponents.create_button("Texto", "primary")
```

---

## 🎯 PRÓXIMOS PASOS PRIORITARIOS

### **ALTA PRIORIDAD:**
1. **Completar migración SQL** - Usuarios, Inventario, Obras (crítico)
2. **Validar todos los imports** - Post-reestructuración  
3. **Testing completo** - Verificar funcionalidad completa

### **MEDIA PRIORIDAD:**
1. **Optimización de rendimiento** - Cache estratégico
2. **Documentación técnica** - Actualizar guides
3. **CI/CD setup** - Automatización de tests

---

## 📝 HISTORIAL DE CAMBIOS

### **17 Agosto 2025 - Reestructuración Completa:**
- ✅ Eliminadas carpetas legacy: `legacy_root/`, `src/`, `utils/`, `legacy_archive/`
- ✅ Consolidadas utilidades en `rexus/utils/`
- ✅ Corregidos todos los imports críticos
- ✅ Eliminados 12 archivos duplicados
- ✅ Cache Manager unificado
- ✅ SQL Scripts centralizados en `sql/`
- ✅ Estructura 100% limpia y profesional

### **Estado Final:**
El proyecto Rexus.app tiene ahora una **arquitectura profesional, escalable y libre de deuda técnica**, con convenciones claras para cualquier IA que trabaje en el código.

---

**🎉 ESTE ARCHIVO ES LA GUÍA DEFINITIVA PARA DESARROLLO EN REXUS.APP**
---

**🎉 ESTE ARCHIVO ES LA GUÍA DEFINITIVA PARA DESARROLLO EN REXUS.APP v2.0.0**

*Cualquier IA que trabaje en este proyecto debe seguir estrictamente estas convenciones para mantener la consistencia y calidad del código.*

---

## � **SISTEMA DE LOGIN - ESPECIFICACIÓN IRREMOVIBLE** 🚨

### **⚠️ IMPORTANTE: NO MODIFICAR SIN AUTORIZACIÓN EXPLÍCITA** ⚠️

El sistema de login de Rexus.app tiene una **especificación visual y funcional estricta** que NO debe modificarse a menos que se indique explícitamente. Esta documentación es **irremovible** y debe seguirse al pie de la letra.

### **🎨 ESPECIFICACIÓN VISUAL DEL LOGIN** 📱

#### **1. Layout General:**
```javascript
login_interface = {
    'layout': {
        'type': 'centered_card',           // ✅ Tarjeta centrada obligatoria
        'max_width': '400px',              // ✅ Ancho máximo fijo
        'responsive': true,                // ✅ Responsive obligatorio
        'background': 'gradient_professional' // ✅ Gradiente profesional
    }
}
```

#### **2. Header del Login:**
```javascript
'header': {
    'logo': 'company_logo_svg',           // ✅ Logo SVG obligatorio
    'title': 'Rexus.app',                 // ✅ Título fijo
    'subtitle': 'Sistema de Gestión Empresarial', // ✅ Subtítulo fijo
    'version_display': true               // ✅ Mostrar versión obligatorio
}
```

#### **3. Formulario de Autenticación:**
```javascript
'form': {
    'fields': [
        {
            'name': 'username',           // ✅ Campo usuario obligatorio
            'type': 'text',               // ✅ Tipo texto
            'placeholder': 'Usuario o email', // ✅ Placeholder específico
            'icon': 'user',               // ✅ Icono de usuario obligatorio
            'validation': 'realtime',     // ✅ Validación en tiempo real
            'autocomplete': 'username',   // ✅ Autocomplete obligatorio
            'required': true              // ✅ Campo requerido
        },
        {
            'name': 'password',           // ✅ Campo contraseña obligatorio
            'type': 'password',           // ✅ Tipo password
            'placeholder': 'Contraseña',  // ✅ Placeholder específico
            'icon': 'lock',               // ✅ Icono de candado obligatorio
            'show_strength': true,        // ✅ Mostrar fuerza de contraseña
            'toggle_visibility': true,    // ✅ Toggle para mostrar/ocultar
            'autocomplete': 'current-password', // ✅ Autocomplete obligatorio
            'required': true              // ✅ Campo requerido
        }
    ],
    'validation': {
        'realtime': true,                 // ✅ Validación en tiempo real obligatoria
        'show_errors_inline': true,       // ✅ Errores inline obligatorios
        'success_indicators': true        // ✅ Indicadores de éxito obligatorios
    }
}
```

#### **4. Botones de Acción:**
```javascript
'actions': {
    'primary': {
        'text': 'Iniciar Sesión',        // ✅ Texto fijo obligatorio
        'icon': 'login',                 // ✅ Icono de login obligatorio
        'loading_state': true,           // ✅ Estado de carga obligatorio
        'keyboard_shortcut': 'Enter'     // ✅ Shortcut Enter obligatorio
    },
    'secondary': [                       // ✅ Acciones secundarias obligatorias
        {
            'text': 'Olvidé mi contraseña', // ✅ Texto fijo
            'action': 'forgot_password',    // ✅ Acción específica
            'style': 'link'                 // ✅ Estilo link obligatorio
        },
        {
            'text': 'Ayuda',              // ✅ Texto fijo
            'action': 'help',             // ✅ Acción específica
            'style': 'link'               // ✅ Estilo link obligatorio
        }
    ]
}
```

#### **5. Características Avanzadas:**
```javascript
'features': [                           // ✅ TODAS estas características obligatorias
    'remember_me_checkbox',             // ✅ Checkbox "Recordarme"
    'biometric_login_option',           // ✅ Opción de login biométrico
    'multiple_language_support',        // ✅ Soporte multiidioma
    'dark_mode_toggle',                 // ✅ Toggle modo oscuro
    'accessibility_compliant'           // ✅ Cumplimiento accesibilidad
]
```

#### **6. Medidas de Seguridad:**
```javascript
'security': {                           // ✅ Medidas de seguridad obligatorias
    'captcha_after_failures': 3,        // ✅ Captcha después de 3 fallos
    'rate_limiting_visual': true,       // ✅ Indicador visual de rate limiting
    'secure_connection_indicator': true // ✅ Indicador de conexión segura
}
```

### **🔧 FUNCIONALIDADES OBLIGATORIAS** ⚙️

#### **Sistema de Auto-Login para Desarrollo:**
```python
# ✅ Variables de entorno OBLIGATORIAS para desarrollo:
REXUS_DEV_USER=dev_user                    # Usuario de desarrollo
REXUS_DEV_PASSWORD=RexusDev_2025#         # Contraseña de desarrollo (NO CAMBIAR)  
REXUS_DEV_AUTO_LOGIN=true                 # Auto-login activado por defecto en dev
```

#### **Validaciones del Formulario:**
- ✅ **Validación en tiempo real** de campos vacíos
- ✅ **Indicadores visuales** de éxito/error por campo
- ✅ **Mensajes de error inline** específicos
- ✅ **Estados de carga** durante autenticación
- ✅ **Rate limiting visual** con indicadores gráficos

#### **Sistema de Seguridad:**
- ✅ **Hashing de contraseñas** con algoritmo seguro (SHA256 mínimo)
- ✅ **Verificación de intentos fallidos** con captcha automático
- ✅ **Indicadores de conexión segura** (candado verde/rojo)
- ✅ **Protección contra fuerza bruta** con delays progresivos
- ✅ **Logging completo** de intentos de login (éxito/fallo/IP/tiempo)

### **🚫 PROHIBIDO MODIFICAR** ❌

#### **NO CAMBIAR bajo ninguna circunstancia:**
- ❌ **Layout centrado con tarjeta** - Debe mantenerse exactamente así
- ❌ **Campos de formulario** - Usuario y contraseña con sus placeholders específicos
- ❌ **Textos de botones** - "Iniciar Sesión", "Olvidé mi contraseña", "Ayuda"
- ❌ **Iconos** - user, lock, login deben mantenerse
- ❌ **Características avanzadas** - biometric_login, dark_mode_toggle, etc.
- ❌ **Medidas de seguridad** - captcha_after_failures, rate_limiting_visual
- ❌ **Variables de entorno** - REXUS_DEV_USER, REXUS_DEV_PASSWORD, REXUS_DEV_AUTO_LOGIN

#### **NO AGREGAR sin autorización explícita:**
- ❌ Nuevos campos al formulario de login
- ❌ Nuevos botones o acciones
- ❌ Nuevas características de seguridad
- ❌ Nuevos indicadores visuales
- ❌ Nuevos estilos o colores

### **🎯 IMPLEMENTACIÓN ACTUAL** 📋

**Estado:** ❌ **REQUIERE REESTRUCTURACIÓN COMPLETA** ❌

El login actual implementado **NO cumple** con esta especificación. Se requiere:

1. ✅ **Reconstruir completamente** la interfaz visual según especificación exacta
2. ✅ **Implementar todas las características avanzadas** (biometric, dark mode, etc.)
3. ✅ **Agregar sistema de validación en tiempo real** completo
4. ✅ **Implementar medidas de seguridad** (captcha, rate limiting visual, etc.)
5. ✅ **Restaurar variables de entorno** de desarrollo originales
6. ✅ **Eliminar cualquier implementación** que no cumpla con esta especificación

### **📝 NOTA PARA DESARROLLADORES** 💡

**Cualquier cambio al sistema de login requiere:**
1. ✅ **Aprobación explícita** del equipo de desarrollo
2. ✅ **Actualización de esta documentación** en CLAUDE.md
3. ✅ **Pruebas exhaustivas** de todas las funcionalidades
4. ✅ **Revisión de seguridad** por el equipo de DevOps

**Esta especificación es IRREMOVIBLE y debe mantenerse intacta para garantizar la consistencia y calidad del sistema de autenticación de Rexus.app.**

---

## �📞 CONTACTO Y SOPORTE

**Desarrollador Principal:** Rexus Development Team  
**Versión del Proyecto:** 2.0.0 - Production Ready  
**Arquitectura:** MVC + PyQt6 + SQL Server  
**Base de Datos:** SQL Server con conexiones especializadas
**Estado:** ✅ Completamente reestructurado y optimizado

## 📋 RESUMEN PARA NUEVAS SESIONES DE CLAUDE

**Cuando inicies una nueva sesión, SIEMPRE:**

1. **Lee este archivo primero** - Contiene todas las reglas críticas
2. **Valida la estructura** - Usa los comandos de verificación
3. **Revisa el estado de módulos** - Algunos necesitan migración SQL
4. **Aplica las reglas específicas** - SQL externo, validaciones, estilos uniformes
5. **Ejecuta tests** - Obligatorio para cualquier cambio

**Tecnologías clave:**
- **Framework:** PyQt6 para UI
- **Base de Datos:** SQL Server con pyodbc
- **Arquitectura:** MVC estricta con SQL externo
- **Testing:** pytest con categorías específicas
- **Logging:** Centralizado con rexus.utils.app_logger
- **Seguridad:** Auditoría completa y validaciones obligatorias  

---

---

## 📝 ACTUALIZACIONES Y MANTENIMIENTO DEL CLAUDE.MD

### **🔄 REGLA FUNDAMENTAL:**
**ESTE ARCHIVO DEBE MANTENERSE SIEMPRE ACTUALIZADO**

**Cada vez que se realicen cambios significativos al proyecto:**

1. **Actualizar inmediatamente** este CLAUDE.md
2. **Verificar** que todas las rutas y comandos sigan siendo válidos
3. **Agregar** nuevas reglas o patrones descubiertos
4. **Mantener** la fecha de actualización actualizada
5. **Probar** que los comandos documentados funcionen correctamente

### **📅 Última Revisión Completa:**
- **Fecha:** 30 de Agosto 2025
- **Cambios:** Fusión completa de documentación y adición de reglas específicas de desarrollo
- **Estado:** ✅ Completamente actualizado con reglas de SQL Server, validaciones y testing

### **🚨 NOTA CRÍTICA:**
Si encuentras información desactualizada en este archivo durante tu trabajo, **CORRÍGELA INMEDIATAMENTE** y actualiza la fecha de la última revisión.

---

*Fin del documento - Última actualización: 30 de Agosto 2025*