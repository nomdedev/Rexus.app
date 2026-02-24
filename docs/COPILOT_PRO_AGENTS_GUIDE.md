# 🤖 Usar Agentes de Rexus.app con Copilot Pro y Pixel Agents

Guía completa para integrar y usar los agentes especializados de Rexus.app desde tu entorno de desarrollo.

---

## 📋 Tabla de Contenidos

1. [¿Qué son los Agentes de Rexus.app?](#qué-son)
2. [Integración con Pixel Agents](#pixel-agents)
3. [Uso desde Copilot Pro](#copilot-pro)
4. [Ejemplos Prácticos](#ejemplos)
5. [Referencia de Agentes](#referencia)

---

## ¿Qué son los Agentes de Rexus.app? {#qué-son}

Los **Agentes de Rexus.app** son asistentes de IA especializados que automatizan tareas dentro de tu aplicación:

### 🎯 Funciones Principales

| Función | Descripción |
|---------|-------------|
| **Análisis** | Analizan código, datos, rendimiento |
| **Reportes** | Generan reportes detallados en JSON |
| **Mejoras** | Proponen optimizaciones específicas |
| **Ejecución** | Implementan cambios autorizados |

### 📦 Agentes Disponibles

```python
# Agentes por módulo (4)
from rexus.agents import InventarioAgent  # 📦 Gestión de stock
from rexus.agents import ObrasAgent       # 🏗️ Gestión de proyectos
from rexus.agents import UsuariosAgent    # 👥 Gestión de usuarios
from rexus.agents import ComprasAgent     # 🛒 Gestión de compras

# Agentes de tareas (2)
from rexus.agents import DatabaseAgent      # 🗄️ Optimización BD
from rexus.agents import CodeQualityAgent   # 🔍 Calidad de código

# Agentes especializados (5)
from rexus.agents import SkillExecutorAgent       # ⚡ Skills de Claude
from rexus.agents import TestGeneratorAgent       # 🧪 Generador de tests
from rexus.agents import SecurityAuditAgent       # 🔒 Auditoría de seguridad
from rexus.agents import PerformanceOptimizerAgent # ⚡ Optimización
from rexus.agents import SystemMonitorAgent       # 📊 Monitoreo
```

---

## Integración con Pixel Agents {#pixel-agents}

### ✅ Configuración Automática

El sistema ya está configurado para funcionar con Pixel Agents:

**Archivo:** `.vscode/pixel-agents.json`

Este archivo contiene la definición de los 11 agentes para que Pixel Agents pueda mostrarlos en su panel.

### 🔄 Sincronización Manual

Si necesitas sincronizar los agentes:

```python
from rexus.agents.pixel_bridge import sync_rexus_agents_with_pixel

# Sincronizar agentes con Pixel Agents
sync_rexus_agents_with_pixel()
```

O ejecutar desde terminal:

```bash
python -c "from rexus.agents.pixel_bridge import sync_rexus_agents_with_pixel; sync_rexus_agents_with_pixel()"
```

### 👀 Ver Agentes en Pixel Agents

1. **Abre VS Code**
2. **Busca el panel de Pixel Agents** (generalmente en la barra lateral)
3. **Verás los 11 agentes de Rexus.app** con sus iconos y descripciones

---

## Uso desde Copilot Pro {#copilot-pro}

### 💡 Sugerencias Automáticas

Cuando trabajes en código relacionado con módulos de Rexus.app, **Copilot Pro sugerirá automáticamente** el uso de agentes apropiados:

```python
# Escribes:
async def check_inventory_low_stock():
    # Copilot Pro sugerirá:
    # from rexus.agents import InventarioAgent
    # agent = InventarioAgent()
    # response = await agent.analyze('stock', {})
    pass
```

### 🎯 Comandos de Copilot Pro

Puedes pedirle a Copilot Pro:

**Prompt:**
```
"Usa InventarioAgent para analizar el stock bajo"
```

**Copilot Pro generará:**
```python
from rexus.agents import InventarioAgent

agent = InventarioAgent()
response = await agent.analyze('stock', {'threshold': 10})
low_stock = response.metadata['analysis']['stock']['low_stock']

print(f"Productos con stock bajo: {len(low_stock)}")
```

### 🔧 Auto-Import

Copilot Pro automáticamente importará los agentes necesarios:

```python
# Solo escribe:
agent = InventarioAgent()

# Copilot Pro añadirá:
# from rexus.agents import InventarioAgent
```

---

## Ejemplos Prácticos {#ejemplos}

### 📦 Ejemplo 1: Análisis de Inventario

```python
from rexus.agents import InventarioAgent

async def analizar_stock_bajo():
    """Analizar productos con stock bajo"""
    agent = InventarioAgent()

    # Analizar stock
    response = await agent.analyze(
        target='stock',
        context={'days': 30, 'threshold': 10}
    )

    # Obtener resultados
    analysis = response.metadata['analysis']
    low_stock = analysis['stock']['low_stock']

    # Generar reporte
    report = await agent.generate_report(analysis)
    print(f"Productos con stock bajo: {len(low_stock)}")

    return low_stock
```

### 🗄️ Ejemplo 2: Optimización de Base de Datos

```python
from rexus.agents import DatabaseAgent

async def optimizar_consultas_lentas():
    """Identificar y optimizar consultas lentas"""
    agent = DatabaseAgent()

    # Analizar rendimiento
    response = await agent.analyze('queries', {})
    analysis = response.metadata['analysis']

    slow_queries = analysis['queries']['most_expensive']

    # Obtener recomendaciones
    improvements = await agent.propose_improvements(analysis)

    print(f"Consultas lentas encontradas: {len(slow_queries)}")
    print(f"Optimizaciones sugeridas: {len(improvements)}")

    return improvements
```

### 🔒 Ejemplo 3: Auditoría de Seguridad

```python
from rexus.agents import SecurityAuditAgent

async def auditar_vulnerabilidades():
    """Auditar seguridad del código"""
    agent = SecurityAuditAgent()

    # Auditar dependencias
    response = await agent.analyze('dependencies', {})
    analysis = response.metadata['analysis']

    vulns = analysis['dependencies']['vulnerable_dependencies']

    # Obtener recomendaciones de seguridad
    improvements = await agent.propose_improvements(analysis)

    print(f"Vulnerabilidades encontradas: {len(vulns)}")
    for improvement in improvements:
        print(f"🚨 {improvement['titulo']}: {improvement['prioridad']}")

    return improvements
```

### 🧪 Ejemplo 4: Generar Tests Automáticamente

```python
from rexus.agents import TestGeneratorAgent

async def generar_tests_para_modulo(modulo: str):
    """Generar tests para un módulo específico"""
    agent = TestGeneratorAgent()

    # Analizar cobertura
    response = await agent.analyze('gaps', {'target': modulo})
    analysis = response.metadata['analysis']

    untested = analysis['gaps']['untested_functions']

    print(f"Funciones sin tests: {len(untested)}")

    # Generar tests para funciones sin testear
    for func in untested:
        await agent.generate_tests(func['file'], test_type='unit')
        print(f"✅ Test generado para: {func['name']}")
```

### ⚡ Ejemplo 5: Integración Completa

```python
from rexus.agents import (
    InventarioAgent,
    DatabaseAgent,
    SecurityAuditAgent
)

async def auditoria_completa_sistema():
    """Ejecutar auditoría completa del sistema"""
    resultados = {}

    # 1. Auditar inventario
    inv_agent = InventarioAgent()
    inv_response = await inv_agent.analyze('all', {})
    resultados['inventario'] = inv_response.metadata['analysis']

    # 2. Auditar base de datos
    db_agent = DatabaseAgent()
    db_response = await db_agent.analyze('all', {})
    resultados['database'] = db_response.metadata['analysis']

    # 3. Auditar seguridad
    sec_agent = SecurityAuditAgent()
    sec_response = await sec_agent.analyze('all', {})
    resultados['security'] = sec_response.metadata['analysis']

    # Generar reportes
    for modulo, analysis in resultados.items():
        print(f"📊 Reporte de {modulo}:")
        print(f"   Análisis completado: {len(analysis)} categorías")

    return resultados
```

---

## Referencia de Agentes {#referencia}

### 📦 InventarioAgent

**Uso:** Gestión de inventario y stock

```python
agent = InventarioAgent()
response = await agent.analyze('stock|productos|movimientos|reservas|all', context)
```

**Targets:**
- `stock` - Análisis de stock y niveles
- `productos` - Catálogo de productos
- `movimientos` - Movimientos de inventario
- `reservas` - Reservas de stock
- `all` - Todos los análisis

### 🗄️ DatabaseAgent

**Uso:** Optimización de base de datos

```python
agent = DatabaseAgent()
response = await agent.analyze('performance|schema|queries|indexes|all', context)
```

**Targets:**
- `performance` - Rendimiento de BD
- `schema` - Estructura de esquema
- `queries` - Consultas SQL
- `indexes` - Índices y optimización

### 🔍 CodeQualityAgent

**Uso:** Análisis de calidad de código

```python
agent = CodeQualityAgent()
response = await agent.analyze('complexity|duplication|smells|coverage|all', context)
```

**Targets:**
- `complexity` - Complejidad ciclomática
- `duplication` - Código duplicado
- `smells` - Code smells
- `coverage` - Cobertura de tests

### 🔒 SecurityAuditAgent

**Uso:** Auditoría de seguridad

```python
agent = SecurityAuditAgent()
response = await agent.analyze('dependencies|code|config|owasp|all', context)
```

**Targets:**
- `dependencies` - Dependencias vulnerables
- `code` - Vulnerabilidades en código
- `config` - Configuraciones de seguridad
- `owasp` - OWASP Top 10

### ⚡ PerformanceOptimizerAgent

**Uso:** Optimización de rendimiento

```python
agent = PerformanceOptimizerAgent()
response = await agent.analyze('database|api|frontend|memory|all', context)
```

**Targets:**
- `database` - Rendimiento de BD
- `api` - Endpoints de API
- `frontend` - Rendimiento frontend
- `memory` - Uso de memoria

### 🧪 TestGeneratorAgent

**Uso:** Generación de tests

```python
agent = TestGeneratorAgent()
response = await agent.analyze('coverage|gaps|quality|all', context)
await agent.generate_tests(archivo, test_type='unit|integration|e2e')
```

**Targets:**
- `coverage` - Cobertura de tests
- `gaps` - Funciones sin testear
- `quality` - Calidad de tests

### 📊 SystemMonitorAgent

**Uso:** Monitoreo del sistema

```python
agent = SystemMonitorAgent()
response = await agent.analyze('cpu|memory|disk|network|health|all', context)
alerts = await agent.check_thresholds(analysis)
```

**Targets:**
- `cpu` - Uso de CPU
- `memory` - Uso de memoria
- `disk` - Uso de disco
- `network` - Tráfico de red
- `health` - Salud general

---

## 💡 Tips y Trucos

### 1. **Combinar Múltiples Agentes**

```python
# Usar múltiples agentes en secuencia
inv_agent = InventarioAgent()
db_agent = DatabaseAgent()

# Analizar inventario
inv_response = await inv_agent.analyze('stock', {})

# Optimizar BD basado en resultados
db_response = await db_agent.analyze('database', {})
```

### 2. **Guardar Reportes**

```python
import json

agent = InventarioAgent()
response = await agent.analyze('stock', {})

# Guardar reporte en archivo
report = await agent.generate_report(response.metadata['analysis'])
with open('reporte_inventario.json', 'w') as f:
    f.write(report)
```

### 3. **Ejecutar Cambios Aprobados**

```python
agent = DatabaseAgent()

# Obtener mejoras
improvements = await agent.propose_improvements(analysis)

# Ejecutar cambios aprobados
approval = {
    'approved_by': 'admin',
    'at': datetime.now().isoformat(),
    'reason': 'Optimización necesaria'
}

result = await agent.execute_approved_changes(improvements, approval)
```

### 4. **Monitorear Estado de Agentes**

```python
from rexus.agents import get_state_manager

state_mgr = get_state_manager()

# Ver tareas activas
active_tasks = state_mgr.get_active_tasks()

# Ver resumen
summary = state_mgr.get_summary()
print(f"Tareas activas: {summary['active_tasks']}")
```

---

## 🚀 Próximos Pasos

1. **Explora los agentes** - Prueba cada uno con los ejemplos
2. **Revisa Pixel Agents** - Abre el panel en VS Code
3. **Usa con Copilot Pro** - Deja que Copilot sugiera agentes
4. **Crea tus propias tareas** - Combina agentes para flujos complejos

---

## 📚 Recursos Adicionales

- **Documentación principal:** `rexus/agents/README.md`
- **Ejemplos:** `scripts/use_agents_from_copilot.py`
- **Configuración Pixel Agents:** `.vscode/pixel-agents.json`
- **Puente Pixel Agents:** `rexus/agents/pixel_bridge.py`

---

**Versión:** 2.0.0
**Última actualización:** 2025-02-24
**Estado:** ✅ Funcional con Copilot Pro y Pixel Agents
