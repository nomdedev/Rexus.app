# 🚨 **PLAN DE ACCIÓN DE SEGURIDAD CRÍTICO - REXUS.APP**
**Fecha:** 25 de Febrero, 2026  
**Prioridad:** 🔴 **CRÍTICA - EJECUCIÓN INMEDIATA**  
**Tiempo Estimado:** 24-48 horas para resolución crítica

---

## 🎯 **OBJETIVO**

Eliminar todas las vulnerabilidades críticas que permiten acceso inmediato al sistema y compromiso de datos sensibles.

---

## 📋 **RESUMEN DE VULNERABILIDADES CRÍTICAS**

| ID | Vulnerabilidad | Archivo | Línea | Riesgo | Tiempo Resolución |
|----|----------------|---------|-------|--------|------------------|
| CRIT-001 | Credenciales hardcodeadas | `rexus/core/login_dialog.py` | 304 | Acceso inmediato | 30 min |
| CRIT-002 | Auto-login desarrollo | `rexus/core/login_dialog.py` | 448-488 | Bypass autenticación | 1 hora |
| CRIT-003 | SQL Injection | `rexus/repositories/inventario/productos_repository.py` | 71 | Exfiltración datos | 2 horas |
| CRIT-004 | Secrets en .env | `.env` | 1-37 | Compromiso sistema | 4 horas |
| CRIT-005 | Múltiples SQL Injection | Múltiples archivos | Varias | Manipulación BD | 6 horas |

---

## 🔧 **PLAN DE ACCIÓN DETALLADO**

### **FASE 1: ELIMINACIÓN DE ACCESO INMEDIATO (0-2 horas)**

#### **🚨 TAREA 1.1: Eliminar credenciales hardcodeadas**
- **Archivo:** [`rexus/core/login_dialog.py`](rexus/core/login_dialog.py:304)
- **Código vulnerable:**
```python
# ❌ LÍNEA 304 - VULNERABLE
info_label = QLabel("Usuario de prueba: admin / admin")
```
- **Acción correctiva:**
```python
# ✅ LÍNEA 304 - SECURE
# Eliminar completamente la línea de credenciales
# O reemplazar con mensaje genérico
info_label = QLabel("Sistema de Gestión Rexus")
```
- **Verificación:** Compilar y probar que no aparecen credenciales
- **Responsable:** Desarrollador Senior
- **Tiempo:** 30 minutos

#### **🚨 TAREA 1.2: Remover auto-login desarrollo**
- **Archivo:** [`rexus/core/login_dialog.py`](rexus/core/login_dialog.py:448-488)
- **Código vulnerable:**
```python
# ❌ LÍNEAS 448-488 - VULNERABLE
def check_dev_auto_login(self):
    # ... lógica de auto-login
```
- **Acción correctiva:**
```python
# ✅ OPCIÓN 1: Eliminar completamente
# def check_dev_auto_login(self):
#     pass  # Eliminar función

# ✅ OPCIÓN 2: Solo en modo desarrollo estricto
def check_dev_auto_login(self):
    # Verificar entorno de desarrollo seguro
    if not self._is_secure_dev_environment():
        return
    
    # Resto de la lógica solo si es seguro
    # ...

def _is_secure_dev_environment(self):
    """Verifica que estamos en un entorno de desarrollo seguro."""
    return (
        os.getenv('REXUS_ENV') == 'development' and
        os.getenv('REXUS_DEV_MACHINE_ID') == get_secure_machine_id() and
        not os.getenv('REXUS_PRODUCTION_MODE', '').lower() == 'true'
    )
```
- **Verificación:** Probar que auto-login no funciona en producción
- **Responsable:** Desarrollador Senior
- **Tiempo:** 1 hora

### **FASE 2: PROTECCIÓN DE DATOS SENSIBLES (2-6 horas)**

#### **🚨 TAREA 2.1: Mover secrets a gestor seguro**
- **Archivo:** [`.env`](.env)
- **Secrets expuestos:**
```bash
# ❌ VULNERABLE - Exposed in plaintext
DB_PASSWORD=mps.1887
SECRET_KEY=rexus_secret_key_production_2025_secure_random_string_for_encryption
JWT_SECRET_KEY=jwt_rexus_2025_secure_token_generation_key_for_authentication
ENCRYPTION_KEY=encryption_rexus_2025_secure_data_protection_key_for_sensitive_data
```

- **Acción correctiva inmediata:**
```bash
# ✅ PASO 1: Crear .env.example (plantilla segura)
cp .env .env.example
# Editar .env.example eliminando valores reales
```

```bash
# ✅ .env.example - SEGURO
DB_PASSWORD=YOUR_SECURE_PASSWORD_HERE
SECRET_KEY=GENERATE_NEW_SECRET_KEY_HERE
JWT_SECRET_KEY=GENERATE_NEW_JWT_SECRET_HERE
ENCRYPTION_KEY=GENERATE_NEW_ENCRYPTION_KEY_HERE
```

```bash
# ✅ PASO 2: Mover .env real a ubicación segura
mv .env ~/.config/rexus/.env
chmod 600 ~/.config/rexus/.env
```

```bash
# ✅ PASO 3: Actualizar código para leer desde ubicación segura
# Modificar rexus/core/config.py para cargar desde ~/.config/rexus/.env
```

- **Verificación:** Probar que la aplicación lee los secrets desde la nueva ubicación
- **Responsable:** DevOps Engineer + Desarrollador Senior
- **Tiempo:** 4 horas

#### **🚨 TAREA 2.2: Corregir SQL Injection crítico**
- **Archivo:** [`rexus/repositories/inventario/productos_repository.py`](rexus/repositories/inventario/productos_repository.py:71)
- **Código vulnerable:**
```python
# ❌ LÍNEA 71 - VULNERABLE
query += f" ORDER BY {order_by}"
```

- **Acción correctiva:**
```python
# ✅ LÍNEA 71 - SECURE
# Whitelist de columnas permitidas
ALLOWED_ORDER_COLUMNS = [
    'descripcion', 'nombre', 'stock_actual', 'stock_minimo', 
    'precio', 'fecha_creacion', 'fecha_actualizacion', 'categoria'
]

# Ordenamiento seguro
if order_by and order_by in ALLOWED_ORDER_COLUMNS:
    query += f" ORDER BY {order_by}"
else:
    query += " ORDER BY descripcion ASC"  # Default seguro
```

- **Verificación:** Probar con diferentes valores de order_by incluyendo payloads maliciosos
- **Responsable:** Desarrollador Senior
- **Tiempo:** 2 horas

### **FASE 3: BÚSQUEDA Y CORRECCIÓN DE SQL INJECTION ADICIONAL (6-12 horas)**

#### **🚨 TAREA 3.1: Escanear todos los archivos con cursor.execute**
- **Archivos a revisar (basado en informe inteligente):**
  - `rexus/core/backup_manager.py:139`
  - `rexus/core/sql_query_manager.py:151`
  - `rexus/models/productos_model.py:581`
  - `rexus/modules/administracion/recursos_humanos/model.py:329`
  - `rexus/modules/compras/detalle_model.py:126`
  - `rexus/modules/compras/proveedores_model.py:109`
  - Y otros 50+ archivos identificados

- **Proceso de revisión:**
```python
# ✅ Script automatizado para identificar vulnerabilidades
def scan_sql_injection():
    vulnerable_patterns = [
        r'cursor\.execute\(f".*\{.*\}"',
        r'cursor\.execute\(".*".*\+.*\)',
        r'query\s*\+=\s*f".*\{.*\}"',
        r'query\s*\+=\s*".*".*\+.*'
    ]
    
    # Escanear todos los archivos Python
    # Generar reporte de vulnerabilidades
```

- **Acción correctiva para cada caso:**
```python
# ❌ VULNERABLE
query = f"SELECT * FROM {table_name} WHERE id = {user_id}"

# ✅ SECURE
# Opción 1: Whitelist de tablas
ALLOWED_TABLES = ['users', 'products', 'orders']
if table_name in ALLOWED_TABLES:
    query = f"SELECT * FROM {table_name} WHERE id = ?"
    cursor.execute(query, (user_id,))

# ✅ SECURE
# Opción 2: Parámetros siempre
query = "SELECT * FROM products WHERE id = ?"
cursor.execute(query, (user_id,))
```

- **Verificación:** Ejecutar script de prueba con payloads maliciosos
- **Responsable:** Equipo de Desarrollo Completo
- **Tiempo:** 6 horas

---

## 🧪 **PLAN DE PRUEBAS Y VERIFICACIÓN**

### **Pruebas de Seguridad Obligatorias:**

#### **Prueba 1: Acceso sin credenciales**
```bash
# Verificar que no se puede acceder sin credenciales válidas
python -c "
from rexus.core.login_dialog import LoginDialog
import sys
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
login = LoginDialog()
# Verificar que no hay credenciales pre-cargadas
assert login.username_edit.text() == ''
assert login.password_edit.text() == ''
print('✅ Prueba 1 pasada: Sin credenciales pre-cargadas')
"
```

#### **Prueba 2: Auto-login deshabilitado**
```bash
# Verificar que auto-login no funciona
REXUS_DEV_AUTO_LOGIN=true REXUS_DEV_USER=admin REXUS_DEV_PASSWORD=test python test_auto_login.py
# Debe fallar o no auto-loguearse
```

#### **Prueba 3: SQL Injection**
```bash
# Probar payloads maliciosos
python -c "
from rexus.repositories.inventario.productos_repository import ProductoRepository
repo = ProductoRepository(mock_connection)

# Payloads maliciosos
malicious_inputs = [
    '1; DROP TABLE users; --',
    '1\' OR 1=1; --',
    '1 UNION SELECT password FROM users --',
    '1; INSERT INTO users VALUES(\'hacker\',\'password\'); --'
]

for payload in malicious_inputs:
    try:
        result = repo.find_all(order_by=payload)
        print(f'❌ Vulnerable: {payload}')
    except Exception as e:
        print(f'✅ Seguro: {payload} -> {e}')
"
```

#### **Prueba 4: Secrets no expuestos**
```bash
# Verificar que no hay secrets en el código
grep -r "mps\.1887" rexus/ || echo "✅ Sin password expuesto"
grep -r "rexus_secret_key" rexus/ || echo "✅ Sin secret key expuesta"
grep -r "admin / admin" rexus/ || echo "✅ Sin credenciales hardcodeadas"
```

---

## 📊 **MÉTRICAS DE ÉXITO**

### **Antes vs Después:**

| Métrica | Antes | Después (Objetivo) | Estado |
|---------|-------|-------------------|--------|
| **Credenciales hardcodeadas** | 1 | 0 | ✅ Por resolver |
| **Auto-login activo** | ✅ | ❌ | ✅ Por resolver |
| **SQL Injection points** | 56+ | 0 | ✅ Por resolver |
| **Secrets en .env** | 4 | 0 | ✅ Por resolver |
| **Acceso sin autenticación** | ✅ | ❌ | ✅ Por resolver |

---

## 🚀 **EJECUCIÓN DEL PLAN**

### **Timeline Detallado:**

**Hora 0-2: Acceso Inmediato**
- [ ] Eliminar credenciales hardcodeadas (30 min)
- [ ] Remover auto-login desarrollo (1 hora)
- [ ] Pruebas básicas de acceso (30 min)

**Hora 2-6: Datos Sensibles**
- [ ] Mover secrets a ubicación segura (2 horas)
- [ ] Corregir SQL Injection crítico (2 horas)
- [ ] Verificación de protección de datos (2 horas)

**Hora 6-12: SQL Injection General**
- [ ] Escanear todos los archivos (2 horas)
- [ ] Corregir vulnerabilidades encontradas (4 horas)
- [ ] Pruebas exhaustivas de SQL injection (2 horas)

**Hora 12-24: Verificación Final**
- [ ] Pruebas de penetración básicas (4 horas)
- [ ] Verificación de funcionalidad (4 horas)
- [ ] Documentación de cambios (4 horas)
- [ ] Reporte final de seguridad (4 horas)

---

## 📞 **COMUNICACIÓN Y ESCALAMIENTO**

### **Stakeholders a Notificar:**
- **CEO:** Cambios críticos de seguridad
- **CTO:** Impacto técnico y arquitectónico
- **DevOps:** Cambios en infraestructura
- **Equipo Desarrollo:** Nuevas prácticas de seguridad

### **Canales de Comunicación:**
- **Emergencia:** #security-emergency (Slack)
- **Actualizaciones:** #security-updates (Slack)
- **Documentación:** Confluence Security Space
- **Reportes:** security@rexus.app

---

## 🔄 **PLAN DE CONTINGENCIA**

### **Si algo falla:**
1. **Rollback inmediato** usando git
2. **Comunicación a stakeholders** en 15 minutos
3. **Análisis de causa raíz** en 1 hora
4. **Plan de corrección** en 2 horas
5. **Implementación de fix** en 4 horas

### **Comandos de Emergencia:**
```bash
# Rollback a versión segura
git checkout HEAD~1 -- rexus/core/login_dialog.py
git checkout HEAD~1 -- .env

# Reiniciar servicios
systemctl restart rexus-app
docker-compose restart rexus-db

# Verificar estado
curl -f http://localhost:8000/health || echo "❌ Servicio caído"
```

---

## 📋 **CHECKLIST FINAL DE VERIFICACIÓN**

### **Antes de declarar "RESUELTO":**

- [ ] **Credenciales hardcodeadas eliminadas** ✅
- [ ] **Auto-login deshabilitado en producción** ✅
- [ ] **SQL Injection corregido en todos los puntos** ✅
- [ ] **Secrets movidos a ubicación segura** ✅
- [ ] **Pruebas de penetración pasadas** ✅
- [ ] **Funcionalidad verificada** ✅
- [ ] **Documentación actualizada** ✅
- [ ] **Equipo notificado** ✅
- [ ] **Monitorización activa** ✅

---

**🚨 Plan de Acción Crítico creado por Claude Security Review**  
**📅 Fecha: 25 de Febrero, 2026**  
**⏰ Tiempo de Ejecución: 24-48 horas**  
**🎯 Prioridad: CRÍTICA - Sin demoras aceptables**