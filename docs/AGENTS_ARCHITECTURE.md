# 🤖 Arquitectura de Agentes Rexus.app

## Visión General

Se ha creado un **Sistema de Agentes Empresariales** basado en **Microsoft Agent Framework** para realizar auditorías sistemáticas de cada módulo de Rexus.app. Los agentes analizan, proponen mejoras y ejecutan decisiones aprobadas por el consejo superior.

## Estructura Creada

```
rexus/agents/
├── __init__.py                          # Exports principales
├── README.md                            # Guía de uso
├── demo_agents.py                       # Ejemplo de ejecución
│
├── core/
│   ├── __init__.py
│   └── base_agent.py                   # Clase base para todos los agentes
│       ├── AgentConfig                 # Configuración estandarizada
│       ├── AgentResponse                # Respuesta estructurada
│       └── BaseAgent                    # Interfaz base (métodos abstractos)
│
├── module_auditors/
│   ├── __init__.py
│   └── audit_agent.py                  # Auditor especializado
│       └── AuditAgent                   # Audita 7 categorías
│
└── orchestrators/
    ├── __init__.py
    └── orchestrator.py                 # Coordinador central
        └── AgentOrchestrator            # Maneja ciclos completos
```

## Componentes Principales

### 1. **BaseAgent** (`core/base_agent.py`)
- Clase base para todos los agentes
- Define interfaz estándar:
  - `analyze()` - Analizar un objetivo
  - `generate_report()` - Generar reportes
  - `propose_improvements()` - Proponer mejoras
  - `execute_approved_changes()` - Ejecutar cambios autorizados
- Respuestas estructuradas con `AgentResponse`
- Sistema de logging integrado

### 2. **AuditAgent** (`module_auditors/audit_agent.py`)
- Especializado en auditoría de módulos
- Audita 7 categorías:
  - ✓ Funcionalidad
  - ✓ Seguridad
  - ✓ Rendimiento
  - ✓ Código
  - ✓ Base de datos
  - ✓ Documentación
  - ✓ Pruebas

- Un agente por módulo de Rexus.app
- Genera reportes JSON para el consejo
- Propone mejoras específicas
- Ejecuta cambios aprobados

### 3. **AgentOrchestrator** (`orchestrators/orchestrator.py`)
- Coordinador central de todos los agentes
- Funcionalidades:
  - Registrar agentes
  - Ejecutar ciclos de auditoría
  - Recopilar resultados
  - Generar reportes para consejo
  - Ejecutar decisiones del consejo
  - Registrar aprobaciones y cambios

## Flujo de Trabajo

### Ciclo Completo de Auditoría

```
┌─────────────────────────────────────────┐
│  1. CONFIGURACIÓN INICIAL               │
│  - Crear Orchestrator                   │
│  - Registrar Agentes (uno x módulo)     │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│  2. EJECUCIÓN DE AUDITORÍA               │
│  - run_audit_cycle()                    │
│  - Cada agente audita su módulo         │
│  - Audita 7 categorías                  │
│  - Genera hallazgos                     │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│  3. GENERACIÓN DE REPORTES               │
│  - generate_report() por agente         │
│  - Reportes en JSON                     │
│  - Resumen consolidado                  │
│  - Reporte para el consejo               │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│  4. REVISIÓN DEL CONSEJO                 │
│  - Consejo revisa reportes              │
│  - Aprueba o rechaza cambios            │
│  - Define qué implementar               │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│  5. EJECUCIÓN DE DECISIONES              │
│  - execute_council_decisions()          │
│  - Cada agente ejecuta cambios          │
│  - Implementación de mejoras            │
│  - Logging de cambios                   │
└─────────────────────────────────────────┘
```

## Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `rexus/agents/__init__.py` | Exports del sistema |
| `rexus/agents/README.md` | Guía de uso |
| `rexus/agents/demo_agents.py` | Ejemplo de ejecución |
| `rexus/agents/core/base_agent.py` | Clase base |
| `rexus/agents/module_auditors/audit_agent.py` | Agente de auditoría |
| `rexus/agents/orchestrators/orchestrator.py` | Orquestador |
| `scripts/start-agents.py` | Script para iniciar |
| `requirements-agents.txt` | Dependencias |
| `config/agents_config.json` | Configuración |

## Uso Rápido

### Iniciar Sistema Completo
```bash
python scripts/start-agents.py
```

### Uso Programático
```python
from rexus.agents.module_auditors.audit_agent import AuditAgent
from rexus.agents.orchestrators.orchestrator import AgentOrchestrator

# Crear orquestador
orchestrator = AgentOrchestrator("RexusMainOrchestrator")

# Registrar agentes
for module in ['inventario', 'usuarios', 'compras']:
    agent = AuditAgent(module_name=module)
    orchestrator.register_agent(f"audit-{module}", agent)

# Ejecutar ciclo
results = await orchestrator.run_audit_cycle()
```

## Integración con Pixel Agents

Los agentes aparecerán visualizados en el panel de **Pixel Agents** en VS Code mostrando:
- Estado de cada agente
- Módulos auditados
- Reportes generados
- Cambios implementados
- Animaciones de agentes trabajando

## Próximas Etapas

### Fase 1: Integración de Claude AI
- [ ] Implementar llamadas a Claude API en `analyze()`
- [ ] Propuestas inteligentes basadas en análisis real
- [ ] Análisis profundo de código

### Fase 2: Análisis Real de Módulos
- [ ] Leer/parsear código de módulos
- [ ] Ejecutar análisis estáticos (bandit, pylint)
- [ ] Analizar DB schema
- [ ] Revisar tests existentes

### Fase 3: Persistencia
- [ ] Almacenar auditorías en BD
- [ ] Histórico de auditorías
- [ ] Base de datos de decisiones

### Fase 4: UI/Consejo
- [ ] Dashboard de auditorías
- [ ] Interface para consejo
- [ ] Aprobación/rechazo de cambios
- [ ] Historial de decisiones

### Fase 5: Automatización
- [ ] Ciclos automáticos programados
- [ ] Webhooks para eventos
- [ ] Notificaciones de cambios
- [ ] Reportes automáticos

## Configuración

Ver `config/agents_config.json` para:
- Módulos a auditar
- Cronograma de auditorías
- Almacenamiento de reportes
- Retención de datos

## Dependencias

Instalar dependencias de agentes:
```bash
pip install -r requirements-agents.txt
```

Las dependencias incluyen:
- Microsoft Agent Framework (1.0.0b260107)
- Anthropic/OpenAI SDKs
- Async utilities
- Tracing & monitoring

## Registros y Logging

Los logs se guardan en:
- `logs/agents.log` - Logs del sistema
- `logs/error_*.txt` - Errores específicos
- `reports/agents/` - Reportes JSON

## Notas Técnicas

- **Async/Await**: Los agentes usan async para escalabilidad
- **Stateless**: Cada ejecución es independiente
- **Extensible**: Fácil crear nuevos tipos de agentes
- **Auditado**: Todas las acciones quedan registradas
- **JSON**: Reportes en JSON para facilidad de parsing

## Soporte

Para más información:
- Ver [rexus/agents/README.md](../agents/README.md)
- Ver ejemplos en [rexus/agents/demo_agents.py](../agents/demo_agents.py)
- Ver configuración en [config/agents_config.json](../config/agents_config.json)
