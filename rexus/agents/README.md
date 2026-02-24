# Sistema de Agentes Rexus.app

Sistema completo de agentes especializados para automatizar, optimizar y mantener Rexus.app.

## 📁 Estructura del Sistema

```
rexus/agents/
├── core/                       # Componentes base
│   ├── base_agent.py          # Clase base para todos los agentes
│   └── __init__.py
│
├── module_specialists/         # Agentes especializados por módulo
│   ├── inventario_agent.py    # Gestión de inventario y stock
│   ├── obras_agent.py         # Gestión de obras y proyectos
│   ├── usuarios_agent.py      # Gestión de usuarios y seguridad
│   └── compras_agent.py       # Gestión de compras y proveedores
│
├── task_agents/               # Agentes de tareas específicas
│   ├── database_agent.py      # Optimización de base de datos
│   └── code_quality_agent.py  # Análisis de calidad de código
│
├── skill_agents/              # Agentes de integración con skills
│   └── skill_executor_agent.py # Ejecución de skills del sistema
│
├── testing_agents/            # Agentes de testing automatizado
│   └── test_generator_agent.py # Generación de tests
│
├── security_agents/           # Agentes de seguridad
│   └── security_audit_agent.py # Auditoría de seguridad
│
├── optimization_agents/       # Agentes de optimización
│   └── performance_optimizer_agent.py # Optimización de rendimiento
│
├── monitoring_agents/         # Agentes de monitoreo
│   └── system_monitor_agent.py # Monitoreo del sistema
│
├── module_auditors/           # Agentes de auditoría (existentes)
│   └── audit_agent.py         # Auditoría de módulos
│
├── orchestrators/             # Coordinación central
│   └── orchestrator.py        # AgentOrchestrator
│
├── agents_registry.py         # Registro centralizado de agentes
├── state_manager.py           # Gestor de estado de agentes
├── demo_agents.py             # Ejemplos de uso
└── README.md                  # Este archivo
```

## 🤖 Tipos de Agentes

### 1. Agentes Especializados por Módulo

Cada módulo del sistema tiene un agente especializado que conoce su dominio:

| Agente | Responsabilidades |
|--------|------------------|
| **InventarioAgent** | Gestión de stock, productos, reservas, movimientos |
| **ObrasAgent** | Gestión de proyectos, producción, cronogramas, recursos |
| **UsuariosAgent** | Autenticación, permisos, roles, seguridad |
| **ComprasAgent** | Proveedores, pedidos, costos, entregas |

### 2. Agentes de Tareas Específicas

Agentes que realizan tareas técnicas especializadas:

| Agente | Responsabilidades |
|--------|------------------|
| **DatabaseAgent** | Optimización de consultas, migraciones, rendimiento BD |
| **CodeQualityAgent** | Análisis de complejidad, duplicación, code smells |

### 3. Agentes de Skills

Integración con los skills de Claude Code:

| Agente | Responsabilidades |
|--------|------------------|
| **SkillExecutorAgent** | Detectar, ejecutar y encadenar skills disponibles |

### 4. Agentes de Testing

Automatización de pruebas:

| Agente | Responsabilidades |
|--------|------------------|
| **TestGeneratorAgent** | Generación de tests unitarios, integración, cobertura |

### 5. Agentes de Seguridad

Auditoría y protección:

| Agente | Responsabilidades |
|--------|------------------|
| **SecurityAuditAgent** | Vulnerabilidades, OWASP, dependencias, configuraciones |

### 6. Agentes de Optimización

Mejora de rendimiento:

| Agente | Responsabilidades |
|--------|------------------|
| **PerformanceOptimizerAgent** | Análisis de cuellos de botella, optimización BD/frontend |

### 7. Agentes de Monitoreo

Supervisión en tiempo real:

| Agente | Responsabilidades |
|--------|------------------|
| **SystemMonitorAgent** | CPU, memoria, disco, red, alertas |

## 🚀 Uso Rápido

### Desde Copilot Pro / Pixel Agents

¡Sí! Puedes usar los agentes desde **Copilot Pro** y verlos en **Pixel Agents**:

```python
# En tu código, simplemente importa y usa los agentes
from rexus.agents import InventarioAgent, DatabaseAgent, SecurityAuditAgent

# Ejemplo: Analizar inventario
agent = InventarioAgent()
response = await agent.analyze('stock', {'days': 30})
print(response.content)

# Ejemplo: Optimizar base de datos
db_agent = DatabaseAgent()
db_response = await db_agent.analyze('performance', {})
print(db_response.content)
```

**Los agentes aparecerán en:**
- ✅ **Pixel Agents** panel en VS Code (ya configurado en `.vscode/pixel-agents.json`)
- ✅ **Copilot Pro** puede sugerir su uso según el contexto
- ✅ **Autocompletado** te sugerirá los agentes disponibles

### Inicializar Sistema Completo

```python
from rexus.agents import initialize_agents_system

# Inicializar todos los agentes
orchestrator, agents, state_manager = initialize_agents_system()

# Ejecutar análisis con un agente
inventario_agent = agents['module_specialists_inventario']
response = await inventario_agent.analyze('stock', {})
print(response.content)
```

### Usar Agente Específico

```python
from rexus.agents import InventarioAgent

# Crear agente
agent = InventarioAgent()

# Analizar stock
response = await agent.analyze('stock', {'days': 30})

# Generar reporte
report = await agent.generate_report(response.metadata['analysis'])
print(report)
```

### Ejecutar Auditoría Completa

```python
from rexus.agents import AgentOrchestrator, AuditAgent

# Crear orquestador
orchestrator = AgentOrchestrator("MainOrchestrator")

# Registrar agentes de auditoría
for module in ['inventario', 'obras', 'usuarios', 'compras']:
    agent = AuditAgent(module_name=module)
    orchestrator.register_agent(f"audit-{module}", agent)

# Ejecutar ciclo de auditoría
results = await orchestrator.run_audit_cycle(generate_council_report=True)
```

### Usar Registro de Agentes

```python
from rexus.agents import get_agents_registry

registry = get_agents_registry()

# Listar agentes disponibles
all_agents = registry.list_agents()
print(all_agents)

# Crear agente específico
db_agent = registry.create_agent('task_agents', 'database')

# Crear especialista de módulo
inventario_agent = registry.create_module_specialist('inventario')
```

## 📊 Estados de Tareas

Los agentes pueden estar en los siguientes estados:

- `PENDING` - Pendiente de inicio
- `IN_PROGRESS` - En ejecución
- `ANALYZING` - Analizando
- `GENERATING_REPORT` - Generando reporte
- `PROPOSING_CHANGES` - Proponeando cambios
- `EXECUTING` - Ejecutando cambios
- `COMPLETED` - Completado
- `FAILED` - Fallido

## 🔄 Flujo de Trabajo

### 1. Análisis
```python
response = await agent.analyze(target='stock', context={'days': 30})
```

### 2. Generación de Reporte
```python
report = await agent.generate_report(response.metadata['analysis'])
```

### 3. Propuestas de Mejora
```python
improvements = await agent.propose_improvements(response.metadata['analysis'])
```

### 4. Ejecución de Cambios Aprobados
```python
result = await agent.execute_approved_changes(
    changes=improvements,
    approval_metadata={'approved_by': 'admin', 'at': datetime.now()}
)
```

## 🎯 Skills Disponibles

El sistema integra los siguientes skills de Claude Code:

- `keybindings-help` - Personalización de atajos de teclado
- `frontend-design` - Creación de interfaces frontend
- `remotion-best-practices` - Mejores prácticas para Remotion
- `skill-creator` - Creación de nuevos skills
- `vercel-react-best-practices` - Optimización React/Next.js
- `web-design-guidelines` - Revisión de UI

## 📈 Monitoreo de Estado

```python
from rexus.agents import get_state_manager

state_manager = get_state_manager()

# Obtener tareas activas
active_tasks = state_manager.get_active_tasks()

# Obtener resumen
summary = state_manager.get_summary()

# Obtener tareas de un agente
agent_tasks = state_manager.get_agent_tasks('inventario_agent')
```

## 🔧 Configuración

### Configuración Personalizada de Agente

```python
from rexus.agents import AgentConfig, InventarioAgent

config = AgentConfig(
    name="MiAgenteInventario",
    description="Agente personalizado",
    model="claude-opus",
    temperature=0.5,
    max_tokens=8000,
    tags=['inventario', 'custom']
)

agent = InventarioAgent(config=config)
```

## 📝 Extensión

### Crear Nuevo Agente

```python
from rexus.agents import BaseAgent, AgentConfig

class MiAgentePersonalizado(BaseAgent):
    def __init__(self, config=None):
        if config is None:
            config = AgentConfig(
                name="MiAgente",
                description="Descripción",
                tags=['custom']
            )
        super().__init__(config)

    async def analyze(self, target, context):
        # Implementar análisis
        pass

    async def generate_report(self, analysis_data):
        # Generar reporte
        pass

    async def propose_improvements(self, analysis_data):
        # Proponer mejoras
        pass

    async def execute_approved_changes(self, changes, approval_metadata):
        # Ejecutar cambios
        pass
```

### Registrar Agente Personalizado

```python
from rexus.agents import get_agents_registry

registry = get_agents_registry()

# Agregar al catálogo
registry.AGENT_CATALOG['custom_agents'] = {
    'mi_agente': {
        'class': 'MiAgentePersonalizado',
        'module': 'mi_modulo.mi_agente',
        'description': 'Mi agente personalizado',
        'tags': ['custom']
    }
}
```

## 🔐 Seguridad

Los agentes de seguridad realizan:

- Análisis de dependencias vulnerables
- Detección de secretos hardcodeados
- Revisión de configuraciones TLS/CORS
- Verificación de OWASP Top 10
- Análisis de inyecciones SQL/XSS

## 📊 Reporting

Todos los agentes generan reportes en formato JSON con:

- Tipo de reporte
- Fecha y timestamp
- Agente generador
- Análisis completo
- Métricas y scores
- Recomendaciones

## 🚦 Integración con UI

Los estados de los agentes se guardan en `logs/agents_state.json` para:

- Visualización en tiempo real
- Historial de ejecuciones
- Debugging
- Auditoría

## 📦 Próximos Pasos

1. **Integración con Claude API**: Implementar llamadas reales a Claude
2. **Implementación Real**: Completar métodos auxiliares con lógica real
3. **UI Dashboard**: Crear panel de visualización de agentes
4. **Scheduling**: Implementar ejecución periódica de agentes
5. **Notificaciones**: Enviar alertas basadas en resultados de agentes
6. **Machine Learning**: Aprender de decisiones anteriores

## 📚 Archivos Relacionados

- `rexus/bootstrap.py` - Inicialización de agentes al inicio
- `main.py` - Punto de entrada de la aplicación
- `pyproject.toml` - Dependencias del proyecto

---

**Versión**: 2.0.0
**Última actualización**: 2026-02-24
**Estado**: En desarrollo
