"""
Script para ejecutar la auditoría exhaustiva de Rexus.app
Utiliza el Master Orchestrator para coordinar todos los agentes
"""

import sys
import os
import asyncio
from pathlib import Path

# Fijar encoding para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from rexus.agents.orchestrators.master_orchestrator import MasterOrchestrator
from rexus.agents.module_auditors.audit_agent import AuditAgent


async def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🎯 ORQUESTADOR MAESTRO - AUDITORÍA EXHAUSTIVA REXUS.APP")
    print("="*80 + "\n")

    # Crear orquestador maestro
    orchestrator = MasterOrchestrator(project_root=root)

    # Registrar agentes de auditoría para cada módulo
    modules_to_audit = [
        'obras',
        'inventario',
        'herrajes',
        'vidrios',
        'logística',
        'pedidos',
        'compras',
        'administración',
        'mantenimiento',
        'auditoría',
        'usuarios',
        'configuración',
        'notificaciones'
    ]

    print(f"[*] Registrando {len(modules_to_audit)} agentes especializados...\n")

    for module_name in modules_to_audit:
        agent = AuditAgent(module_name=module_name)
        agent_id = f"audit-{module_name}"
        orchestrator.register_agent(agent_id, agent)
        print(f"    ✅ {agent_id:30s} - Módulo: {module_name}")

    print(f"\n[OK] {len(modules_to_audit)} agentes registrados exitosamente")
    print(f"[OK] Orquestador Maestro inicializado: {orchestrator.name}\n")

    # Mostrar estado inicial
    status = orchestrator.get_orchestrator_status()
    print("[*] Estado del Orquestador:")
    print(f"    • Nombre: {status['nombre']}")
    print(f"    • Agentes activos: {status['total_agentes']}")
    print(f"    • Sistema listo para auditoría exhaustiva\n")

    # Ejecutar auditoría exhaustiva
    print("="*80)
    print("[*] INICIANDO AUDITORÍA EXHAUSTIVA")
    print("="*80 + "\n")

    try:
        # Ejecutar auditoría completa
        report = await orchestrator.perform_comprehensive_audit()

        print("\n" + "="*80)
        print("✅ AUDITORÍA EXHAUSTIVA COMPLETADA")
        print("="*80)

        # Mostrar resumen ejecutivo
        summary = report['executive_summary']
        health = summary['overall_health_score']

        print(f"\n📊 RESUMEN EJECUTIVO:")
        print(f"    • Módulos analizados:     {summary['total_modules_analyzed']}")
        print(f"    • Auditorías completadas: {summary['audits_completed']}")
        print(f"    • Auditorías fallidas:    {summary['audits_failed']}")
        print(f"    • Archivos analizados:    {summary['total_files_analyzed']}")
        print(f"    • Frameworks detectados:  {', '.join(summary['frameworks_detected']) if summary['frameworks_detected'] else 'N/A'}")

        print(f"\n⚠️  HALLAZGOS POR SEVERIDAD:")
        print(f"    🔴 Críticos:             {summary['critical_findings']}")
        print(f"    🟠 Alta prioridad:       {summary['high_priority_findings']}")
        print(f"    🟡 Media prioridad:      {summary['medium_priority_findings']}")
        print(f"    🟢 Baja prioridad:       {summary.get('low_priority_findings', 0)}")

        print(f"\n💯 SCORE DE SALUD DEL PROYECTO:")
        print(f"    {health['score']}/100 - {health['category']}")

        # Mostrar recomendaciones prioritarias
        print(f"\n🎯 TOP 10 RECOMENDACIONES PRIORITARIAS:")
        recommendations = report['prioritized_recommendations'][:10]
        for i, rec in enumerate(recommendations, 1):
            finding = rec['finding']
            severity_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(rec['severity'], '⚪')

            titulo = finding.get('título') or finding.get('title') or finding.get('description') or 'Sin título'
            prioridad = finding.get('prioridad', 'N/A')

            print(f"  {i:2d}. {severity_icon} [{rec['severity'].upper():8s}] {titulo}")
            if finding.get('descripción') or finding.get('description'):
                desc = finding.get('descripción') or finding.get('description')
                print(f"      {desc}")

        # Mostrar plan de acción inmediato
        print(f"\n📋 ACCIONES INMEDIATAS RECOMENDADAS:")
        for action in report['action_plan']['immediate_actions']:
            print(f"  • {action['action']}")
            print(f"    Prioridad: {action['priority']}")
            print(f"    Tiempo estimado: {action['estimated_time']}")
            print(f"    Recursos: {action['resources']}\n")

        print("="*80)
        print("📄 REPORTES GENERADOS")
        print("="*80)
        print("[*] Reporte completo guardado en: reports/audits/")
        print("[*] Consulta el JSON completo para todos los detalles")
        print("[*] Los hallazgos están disponibles en Pixel Agents\n")

    except Exception as e:
        print(f"\n[ERROR] Error durante la auditoría: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INFO] Auditoría interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
