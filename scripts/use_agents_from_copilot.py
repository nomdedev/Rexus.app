"""
Ejemplo de uso de agentes de Rexus.app desde Copilot Pro/Pixel Agents

Este script demuestra cómo interactuar con los agentes que creamos
directamente desde tu entorno de desarrollo
"""

import asyncio
import sys
from pathlib import Path

# Agregar ruta del proyecto
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from rexus.agents import (
    InventarioAgent,
    ObrasAgent,
    DatabaseAgent,
    CodeQualityAgent,
    TestGeneratorAgent,
    SecurityAuditAgent,
    PerformanceOptimizerAgent,
    SystemMonitorAgent
)


async def example_use_inventario_agent():
    """Ejemplo: Usar agente de inventario"""
    print("\n" + "="*80)
    print("📦 EJEMPLO: InventarioAgent")
    print("="*80)

    agent = InventarioAgent()

    # Analizar stock
    response = await agent.analyze('stock', {'days': 30})
    print(f"✅ Análisis completado: {response.content}")

    # Generar reporte
    report = await agent.generate_report(response.metadata['analysis'])
    print(f"📄 Reporte generado: {len(report)} caracteres")

    # Obtener mejoras
    improvements = await agent.propose_improvements(response.metadata['analysis'])
    print(f"💡 Mejoras sugeridas: {len(improvements)}")
    for improvement in improvements:
        print(f"   - {improvement['titulo']}: {improvement['prioridad']} prioridad")


async def example_use_database_agent():
    """Ejemplo: Usar agente de base de datos"""
    print("\n" + "="*80)
    print("🗄️ EJEMPLO: DatabaseAgent")
    print("="*80)

    agent = DatabaseAgent()

    # Analizar rendimiento de BD
    response = await agent.analyze('performance', {})
    print(f"✅ Análisis completado: {response.content}")

    # Obtener recomendaciones
    improvements = await agent.propose_improvements(response.metadata['analysis'])
    print(f"💡 Optimizaciones sugeridas: {len(improvements)}")


async def example_use_security_agent():
    """Ejemplo: Usar agente de seguridad"""
    print("\n" + "="*80)
    print("🔒 EJEMPLO: SecurityAuditAgent")
    print("="*80)

    agent = SecurityAuditAgent()

    # Auditar dependencias
    response = await agent.analyze('dependencies', {})
    print(f"✅ Auditoría completada: {response.content}")

    # Obtener vulnerabilidades
    improvements = await agent.propose_improvements(response.metadata['analysis'])
    print(f"🚨 Issues de seguridad encontrados: {len(improvements)}")
    for issue in improvements:
        print(f"   - {issue['titulo']}: {issue['prioridad']} prioridad")


async def example_use_test_generator():
    """Ejemplo: Usar generador de tests"""
    print("\n" + "="*80)
    print("🧪 EJEMPLO: TestGeneratorAgent")
    print("="*80)

    agent = TestGeneratorAgent()

    # Analizar cobertura de tests
    response = await agent.analyze('coverage', {})
    print(f"✅ Análisis completado: {response.content}")

    # Generar mejoras
    improvements = await agent.propose_improvements(response.metadata['analysis'])
    print(f"💡 Sugerencias de testing: {len(improvements)}")


async def example_use_code_quality():
    """Ejemplo: Usar agente de calidad de código"""
    print("\n" + "="*80)
    print("🔍 EJEMPLO: CodeQualityAgent")
    print("="*80)

    agent = CodeQualityAgent()

    # Analizar complejidad
    response = await agent.analyze('complexity', {'target': 'rexus/modules'})
    print(f"✅ Análisis completado: {response.content}")

    # Obtener refactorizaciones
    improvements = await agent.propose_improvements(response.metadata['analysis'])
    print(f"♻️ Refactorizaciones sugeridas: {len(improvements)}")


async def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "="*80)
    print("🤖 EJEMPLOS DE USO DE AGENTES REXUS.APP")
    print("Desde Copilot Pro / Pixel Agents")
    print("="*80)

    # Ejecutar ejemplos
    await example_use_inventario_agent()
    await example_use_database_agent()
    await example_use_security_agent()
    await example_use_test_generator()
    await example_use_code_quality()

    print("\n" + "="*80)
    print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
    print("="*80)
    print("\n💡 Para usar estos agentes en tu código:")
    print("   from rexus.agents import InventarioAgent")
    print("   agent = InventarioAgent()")
    print("   response = await agent.analyze('stock', {})")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Ejecución interrumpida")
        sys.exit(0)
