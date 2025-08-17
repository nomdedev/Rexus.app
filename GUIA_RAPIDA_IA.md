# 🤖 GUÍA RÁPIDA PARA IAs - REXUS.APP v2.0.0

## 🚨 **ANTES DE TOCAR CUALQUIER CÓDIGO - LEE ESTO**

### ✅ **EL PROYECTO HA SIDO COMPLETAMENTE REESTRUCTURADO (17 AGO 2025)**

**NUNCA uses imports legacy** - Han sido eliminados:
```python
# 🚫 PROHIBIDO (ELIMINADOS):
from legacy_root.*
from src.*
from utils.* (nivel raíz)

# ✅ USAR SIEMPRE:
from rexus.core.*
from rexus.utils.*
from rexus.modules.*
```

---

## 📁 **ESTRUCTURA ACTUAL (ÚNICA VÁLIDA)**

```
rexus.app/
├── main.py                    # ✅ ÚNICO punto de entrada
├── rexus/                     # ✅ TODO el código aquí
│   ├── core/                 # Sistema central
│   ├── utils/                # ✅ TODAS las utilidades
│   ├── modules/              # Módulos de negocio
│   ├── ui/                   # Framework UI
│   └── main/                 # App principal
├── sql/                      # ✅ Scripts SQL centralizados
├── tools/                    # Solo herramientas únicas
├── scripts/                  # Scripts operativos
└── tests/                    # Suite de pruebas
```

---

## 🔧 **COMANDOS OBLIGATORIOS ANTES DE CAMBIAR CÓDIGO**

### 1. **Verificar que no existe el archivo:**
```bash
find . -name "*nombre_archivo*" -type f
```

### 2. **Validar estructura actual:**
```bash
python -c "import rexus; print('✅ OK')"
```

### 3. **Verificar imports:**
```bash
python -c "from rexus.utils.sql_query_manager import SQLQueryManager; print('✅ OK')"
```

---

## 🎯 **PATRONES OBLIGATORIOS**

### **Crear Módulo:**
```python
# model.py - SOLO datos y lógica
from rexus.utils.sql_query_manager import SQLQueryManager
from rexus.utils.app_logger import get_logger

class ModuloModel:
    def __init__(self):
        self.sql_manager = SQLQueryManager()
        self.logger = get_logger(__name__)

# view.py - SOLO interfaz
from rexus.ui.base_module_view import BaseModuleView

class ModuloView(BaseModuleView):
    def __init__(self):
        super().__init__()
        self.setup_ui()

# controller.py - SOLO coordinación
class ModuloController:
    def __init__(self):
        self.model = ModuloModel()
        self.view = ModuloView()
```

### **SQL Externo:**
```python
# ✅ USAR archivos SQL:
resultado = self.sql_manager.ejecutar_consulta_archivo(
    'sql/modulo/consulta.sql',
    {'parametro': valor}
)

# 🚫 NUNCA queries hardcodeadas:
query = f"SELECT * FROM tabla WHERE id = {id}"
```

---

## 📊 **ESTADO ACTUAL**

### ✅ **COMPLETADOS (100%):**
- Herrajes, Vidrios, Compras, Pedidos
- Auditoría, Configuración, Logística, Mantenimiento

### 🔄 **PENDIENTES (SQL Migration):**
- Usuarios, Inventario, Obras

---

## 🚨 **ERRORES COMUNES A EVITAR**

1. **No crear archivos duplicados** - Verificar antes
2. **No usar imports legacy** - Solo `rexus.*`
3. **No hardcodear SQL** - Usar archivos externos
4. **No crear archivos en root** - Solo en subcarpetas

---

## 📞 **ARCHIVOS CLAVE DE REFERENCIA**

- **CLAUDE.md** - Guía completa actualizada
- **Checklist pendientes.md** - Estado actual  
- **REPORTE_LIMPIEZA_DUPLICADOS.md** - Cambios realizados

---

**🎯 REGLA DORADA: Cuando dudes, consulta CLAUDE.md**

*Esta guía asegura que cualquier IA mantenga la consistencia del proyecto reestructurado.*
