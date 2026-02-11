# Plan de Mejora - God Objects
## Rexus.app - Refactorización de Modelos Grandes

**Fecha:** 2025-02-10
**Auditoría:** Basado en INFORME_FINAL_AUDITORIA_COMPLETA.md

---

## 📊 Estado Actual

| Modelo | Líneas | Estado | Submódulos |
|--------|--------|--------|------------|
| **InventarioModel** | 3,149 | ⚠️ God Object | ✅ Ya dividido en managers |
| **UsuariosModel** | 1,790 | ⚠️ God Object | ⚠️ Parcialmente dividido |
| **ObrasModel** | 801 | ✅ Aceptable | ⚠️ Puede mejorar |

---

## ✅ InventarioModel - Ya Mejorado

El modelo de inventario ya tiene una arquitectura de submódulos implementada:

```
rexus/modules/02_inventario/
├── model.py (orquestador con proxies)
└── submodules/
    ├── base_utilities.py
    ├── productos_manager.py
    ├── movimientos_manager.py
    ├── reservas_manager.py
    ├── reportes_manager.py
    ├── categorias_manager.py
    └── consultas_manager.py
```

### Arquitectura Actual
- **Patrón**: Delegation/Proxy
- **Ventajas**: Mantenibilidad, testabilidad, separación de responsabilidades
- **Fallback**: Código de compatibilidad para migración gradual

### Próximos Pasos para Inventario
1. **Eliminar código fallback** una vez validada la migración
2. **Mover lógica de negocio** desde `model.py` a los managers
3. **Optimizar queries** en cada manager especializado

---

## 📋 Plan para UsuariosModel (1,790 líneas)

### Estructura Propuesta

```
rexus/modules/11_usuarios/
├── model.py (orquestador)
└── submodules/
    ├── auth_manager.py (ya existe - actualizar)
    ├── users_manager.py (gestión de usuarios)
    ├── permissions_manager.py (permisos y roles)
    ├── sessions_manager.py (sesiones y tokens)
    └── profiles_manager.py (perfiles de usuario)
```

### Responsabilidades por Módulo

#### auth_manager.py
- Login y logout
- Verificación de contraseñas
- Rate limiting de intentos fallidos
- Bloqueo de cuentas

#### users_manager.py
- CRUD de usuarios
- Gestión de estados (activo/inactivo)
- Validaciones de datos de usuario

#### permissions_manager.py
- Definición de roles y permisos
- Asignación de permisos a usuarios
- Verificación de acceso

#### sessions_manager.py
- Gestión de sesiones activas
- Tokens de recuperación
- Historial de logins

#### profiles_manager.py
- Información personal del usuario
- Preferencias de configuración
- Avatar y metadata

---

## 📋 Plan para ObrasModel (801 líneas)

### Estructura Propuesta

```
rexus/modules/01_obras/
├── model.py (orquestador)
├── produccion/
│   ├── estados_manager.py
│   ├── tareas_manager.py
│   └── cronograma_manager.py
└── presupuestos/
    ├── costos_manager.py
    ├── materiales_manager.py
    └── valuation_manager.py
```

### Responsabilidades por Módulo

#### estados_manager.py
- Gestión de estados de obra
- Transiciones de estado
- Historial de cambios

#### tareas_manager.py
- Tareas de la obra
- Asignación de personal
- Seguimiento de progreso

#### cronograma_manager.py
- Fechas de inicio y fin
- Hitos del proyecto
- Alertas de plazos

#### costos_manager.py
- Presupuesto inicial
- Costos adicionales
- Variaciones de presupuesto

#### materiales_manager.py
- Materiales por obra
- Reservas de inventario
- Consumo real vs estimado

#### valuation_manager.py
- Valorizaciones periódicas
- Certificados de avance
- Estado de pago

---

## 🔄 Estrategia de Migración

### Fase 1: Preparación (1-2 días)
1. Crear estructura de directorios
2. Crear archivos de submódulos vacíos
3. Mapear funciones del model.py a submódulos

### Fase 2: Extracción (3-5 días)
1. Mover código a submódulos respectivos
2. Crear métodos proxy en model.py
3. Mantener código original como fallback

### Fase 3: Validación (2-3 días)
1. Ejecutar tests existentes
2. Crear nuevos tests por submódulo
3. Verificar funcionalidad completa

### Fase 4: Limpieza (1-2 días)
1. Eliminar código fallback
2. Actualizar documentación
3. Eliminar código duplicado

---

## 📝 Plantilla de Submódulo

```python
"""
<Nombre>Manager - Gestor especializado para <funcionalidad>

Responsabilidades:
- <lista de responsabilidades>
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class <Nombre>Manager:
    """Gestor de <funcionalidad>."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor."""
        self.db_connection = db_connection

    def metodo_ejemplo(self, param1: str, param2: int) -> Dict[str, Any]:
        """
        Descripción breve del método.

        Args:
            param1: Descripción
            param2: Descripción

        Returns:
            Diccionario con resultado
        """
        if not self.db_connection:
            return {'success': False, 'error': 'Sin conexión a BD'}

        try:
            # Lógica aquí
            pass
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'error': str(e)}
```

---

## 🎯 Métricas de Éxito

| Métrica | Antes | Después | Objetivo |
|---------|-------|---------|----------|
| Líneas model.py | 3,149 | <500 | -85% |
| Complejidad ciclomática | Alta | Baja | <10 por método |
| Tests por módulo | 0 | >5 | Cobertura >70% |
| Tiempo de ejecución | Baseline | = o < | Sin degradación |

---

## 📅 Cronograma Estimado

| Tarea | Duración | Comienzo | Fin |
|-------|----------|----------|-----|
| UsuariosModel refactor | 8-10 horas | Día 1 | Día 2 |
| ObrasModel refactor | 6-8 horas | Día 3 | Día 4 |
| Validación y tests | 4-6 horas | Día 4 | Día 5 |
| Documentación | 2-3 horas | Día 5 | Día 5 |

**Total estimado:** 20-27 horas (3-4 días)

---

## ✅ Conclusión

El modelo de inventario ya tiene una arquitectura saludable con submódulos especializados.
Los modelos de usuarios y obras requieren una refactorización similar siguiendo el mismo patrón.

La estrategia es usar el patrón Proxy/Delegation para mantener compatibilidad durante la migración.
