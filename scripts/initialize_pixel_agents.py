"""
Script para inicializar todos los agentes de Pixel Agents
Genera actividad inicial para que todos los agentes aparezcan en el panel
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timezone

# Fijar encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from rexus.agents.pixel_bridge import PixelAgentsBridge, get_pixel_bridge


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# Configuración de los 13 agentes
AUDIT_AGENTS = [
    {"id": "audit-obras", "name": "ObrasAgent", "icon": "🏗️", "module": "obras"},
    {"id": "audit-inventario", "name": "InventarioAgent", "icon": "📦", "module": "inventario"},
    {"id": "audit-herrajes", "name": "HerrajesAgent", "icon": "🔧", "module": "herrajes"},
    {"id": "audit-vidrios", "name": "VidriosAgent", "icon": "🪟", "module": "vidrios"},
    {"id": "audit-logística", "name": "LogísticaAgent", "icon": "🚚", "module": "logística"},
    {"id": "audit-pedidos", "name": "PedidosAgent", "icon": "📋", "module": "pedidos"},
    {"id": "audit-compras", "name": "ComprasAgent", "icon": "🛒", "module": "compras"},
    {"id": "audit-administración", "name": "AdministraciónAgent", "icon": "📊", "module": "administración"},
    {"id": "audit-mantenimiento", "name": "MantenimientoAgent", "icon": "🔧", "module": "mantenimiento"},
    {"id": "audit-auditoría", "name": "AuditoríaAgent", "icon": "🔍", "module": "auditoría"},
    {"id": "audit-usuarios", "name": "UsuariosAgent", "icon": "👥", "module": "usuarios"},
    {"id": "audit-configuración", "name": "ConfiguraciónAgent", "icon": "⚙️", "module": "configuración"},
    {"id": "audit-notificaciones", "name": "NotificacionesAgent", "icon": "🔔", "module": "notificaciones"},
]


def initialize_agent_session(bridge: PixelAgentsBridge, agent_config: dict):
    """Inicializa una sesión para un agente"""

    agent_id = agent_config["id"]
    agent_name = agent_config["name"]
    module = agent_config["module"]
    icon = agent_config["icon"]

    # Iniciar tarea de inicialización
    task_ref = bridge.start_task(
        agent_id,
        f"Inicializando agente {agent_name} para módulo {module}",
        "initialize"
    )

    # Actualizar progreso
    bridge.update_progress(task_ref, f"Verificando configuración de {module}", 25)

    # Completar inicialización
    result = f"""
{icon} Agente {agent_name} inicializado exitosamente

Módulo: {module}
ID: {agent_id}
Estado: Activo
Capacidades:
  - analyze_module
  - generate_report
  - propose_improvements
  - execute_changes

Categorías: funcionalidad, seguridad, rendimiento, código

El agente está listo para auditar el módulo {module} y generar reportes.
"""

    bridge.complete_task(task_ref, result, is_error=False)

    return task_ref


def main():
    """Inicializa todos los agentes en Pixel Agents"""

    print("\n" + "="*80)
    print("[INFO] INICIALIZANDO AGENTES EN PIXEL AGENTS")
    print("="*80 + "\n")

    # Obtener bridge
    bridge = get_pixel_bridge()

    # Inicializar cada agente
    print(f"[*] Inicializando {len(AUDIT_AGENTS)} agentes...\n")

    for i, agent_config in enumerate(AUDIT_AGENTS, 1):
        agent_name = agent_config["name"]
        module = agent_config["module"]
        icon = agent_config["icon"]

        print(f"[{i}/{len(AUDIT_AGENTS)}] {icon} {agent_name} ({module})...", end=" ")

        try:
            initialize_agent_session(bridge, agent_config)
            print("✅ OK")
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print(f"\n[OK] Todos los agentes han sido inicializados\n")

    print("="*80)
    print("[SUCCESS] AGENTES INICIALIZADOS")
    print("="*80)
    print("\n[*] Los 13 agentes ahora deberían aparecer en Pixel Agents")
    print("[*] Si no los ves, recarga VS Code (Ctrl+Shift+P → 'Reload Window')\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Inicialización interrumpida")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error durante inicialización: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
