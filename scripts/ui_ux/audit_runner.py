#!/usr/bin/env python3
"""
Ejecutor Principal de Auditorías UI/UX para Rexus.app
Coordina y ejecuta todas las auditorías de experiencia de usuario
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class UIUXAuditRunner:
    """Coordinador de auditorías UI/UX"""

    def __init__(self):
        self.root_path = Path(__file__).parent.parent.parent
        self.scripts_path = Path(__file__).parent
        self.logs_path = self.root_path / "logs"
        self.logs_path.mkdir(exist_ok=True)

        # Scripts de auditoría disponibles
        self.audit_scripts = {
            "consistency": self.scripts_path / "audit_ui_consistency.py",
            "accessibility": self.scripts_path / "audit_accessibility.py",
        }

        self.results = {}

    def ejecutar_auditoria_consistencia(self) -> Dict[str, Any]:
        """Ejecuta auditoría de consistencia UI/UX"""
        print("🎨 Ejecutando auditoría de consistencia UI/UX...")

        try:
            result = subprocess.run(
                [sys.executable, str(self.audit_scripts["consistency"])],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            if result.returncode == 0:
                print("✅ Auditoría de consistencia completada exitosamente")

                # Buscar el archivo de reporte generado
                reporte_files = list(self.logs_path.glob("ui_audit_report_*.json"))
                if reporte_files:
                    latest_report = max(reporte_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_report, "r", encoding="utf-8") as f:
                        return json.load(f)
                else:
                    return {
                        "status": "completed",
                        "issues": [],
                        "output": result.stdout,
                    }
            else:
                print(f"❌ Error en auditoría de consistencia: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "output": result.stdout,
                }

        except Exception as e:
            print(f"❌ Excepción en auditoría de consistencia: {e}")
            return {"status": "exception", "error": str(e)}

    def ejecutar_auditoria_accesibilidad(self) -> Dict[str, Any]:
        """Ejecuta auditoría de accesibilidad"""
        print("♿ Ejecutando auditoría de accesibilidad...")

        try:
            result = subprocess.run(
                [sys.executable, str(self.audit_scripts["accessibility"])],
                capture_output=True,
                text=True,
                cwd=self.root_path,
            )

            if result.returncode == 0:
                print("✅ Auditoría de accesibilidad completada exitosamente")

                # Buscar el archivo de reporte generado
                reporte_files = list(
                    self.logs_path.glob("accessibility_audit_report_*.json")
                )
                if reporte_files:
                    latest_report = max(reporte_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_report, "r", encoding="utf-8") as f:
                        return json.load(f)
                else:
                    return {
                        "status": "completed",
                        "issues": [],
                        "output": result.stdout,
                    }
            else:
                print(f"❌ Error en auditoría de accesibilidad: {result.stderr}")
                return {
                    "status": "error",
                    "error": result.stderr,
                    "output": result.stdout,
                }

        except Exception as e:
            print(f"❌ Excepción en auditoría de accesibilidad: {e}")
            return {"status": "exception", "error": str(e)}

    def analizar_modulo_especifico(self, modulo: str) -> Dict[str, Any]:
        """Analiza un módulo específico en profundidad"""
        print(f"🔍 Análisis específico del módulo: {modulo}")

        modulo_path = self.root_path / "rexus" / "modules" / modulo
        if not modulo_path.exists():
            return {"error": f"Módulo {modulo} no encontrado"}

        # Importar y ejecutar auditorías específicas
        try:
            from audit_accessibility import AccessibilityAuditor
            from audit_ui_consistency import UIConsistencyAuditor

            # Auditoría de consistencia
            consistency_auditor = UIConsistencyAuditor()
            consistency_issues = consistency_auditor.analizar_modulo(modulo_path)

            # Auditoría de accesibilidad
            accessibility_auditor = AccessibilityAuditor()
            accessibility_issues = accessibility_auditor.analizar_modulo(modulo_path)

            return {
                "modulo": modulo,
                "consistency_issues": len(consistency_issues),
                "accessibility_issues": len(accessibility_issues),
                "details": {
                    "consistency": [
                        {
                            "tipo": issue.tipo,
                            "severidad": issue.severidad,
                            "descripcion": issue.descripcion,
                            "archivo": issue.archivo,
                            "linea": issue.linea,
                        }
                        for issue in consistency_issues[:10]  # Limitar para el resumen
                    ],
                    "accessibility": [
                        {
                            "criterio": issue.criterio,
                            "nivel": issue.nivel.value,
                            "severidad": issue.severidad,
                            "descripcion": issue.descripcion,
                            "archivo": issue.archivo,
                            "linea": issue.linea,
                        }
                        for issue in accessibility_issues[
                            :10
                        ]  # Limitar para el resumen
                    ],
                },
            }

        except Exception as e:
            return {"error": f"Error analizando módulo {modulo}: {e}"}

    def generar_reporte_consolidado(self) -> str:
        """Genera un reporte consolidado de todas las auditorías"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_path = self.logs_path / f"ui_ux_consolidated_report_{timestamp}.json"

        # Recopilar estadísticas generales
        total_consistency_issues = 0
        total_accessibility_issues = 0
        score_promedio = 0
        modulos_analizados = set()

        if "consistency" in self.results and "issues" in self.results["consistency"]:
            total_consistency_issues = len(self.results["consistency"]["issues"])
            if "modulos_analizados" in self.results["consistency"]:
                modulos_analizados.update(
                    self.results["consistency"]["modulos_analizados"]
                )

        if (
            "accessibility" in self.results
            and "issues" in self.results["accessibility"]
        ):
            total_accessibility_issues = len(self.results["accessibility"]["issues"])
            if "score_accesibilidad" in self.results["accessibility"]:
                score_promedio = self.results["accessibility"]["score_accesibilidad"]
            if "modulos_analizados" in self.results["accessibility"]:
                modulos_analizados.update(
                    self.results["accessibility"]["modulos_analizados"]
                )

        # Calcular score general UI/UX
        score_general = self._calcular_score_general()

        # Generar recomendaciones consolidadas
        recomendaciones = self._generar_recomendaciones_consolidadas()

        reporte_consolidado = {
            "timestamp": datetime.now().isoformat(),
            "resumen_ejecutivo": {
                "modulos_analizados": len(modulos_analizados),
                "total_issues_consistencia": total_consistency_issues,
                "total_issues_accesibilidad": total_accessibility_issues,
                "score_accesibilidad": score_promedio,
                "score_general_ui_ux": score_general,
                "nivel_prioridad": self._determinar_nivel_prioridad(),
            },
            "resultados_detallados": self.results,
            "recomendaciones_consolidadas": recomendaciones,
            "plan_accion": self._generar_plan_accion(),
        }

        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(reporte_consolidado, f, indent=2, ensure_ascii=False)

        print(f"📄 Reporte consolidado guardado en: {reporte_path}")
        return str(reporte_path)

    def _calcular_score_general(self) -> float:
        """Calcula un score general de UI/UX"""
        scores = []

        # Score de consistencia (basado en cantidad de issues)
        if (
            "consistency" in self.results
            and "estadisticas" in self.results["consistency"]
        ):
            total_issues = self.results["consistency"]["estadisticas"].get(
                "total_issues", 0
            )
            modulos = self.results["consistency"]["estadisticas"].get(
                "modulos_analizados", 1
            )
            # Score inverso: menos issues = mejor score
            consistency_score = max(0, 100 - (total_issues / modulos * 5))
            scores.append(consistency_score)

        # Score de accesibilidad
        if (
            "accessibility" in self.results
            and "score_accesibilidad" in self.results["accessibility"]
        ):
            scores.append(self.results["accessibility"]["score_accesibilidad"])

        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def _determinar_nivel_prioridad(self) -> str:
        """Determina el nivel de prioridad de las mejoras"""
        issues_criticos = 0
        issues_altos = 0

        # Contar issues críticos y altos
        for audit_type, result in self.results.items():
            if "issues" in result:
                for issue in result["issues"]:
                    severidad = issue.get("severidad", "")
                    if severidad == "critical":
                        issues_criticos += 1
                    elif severidad == "high":
                        issues_altos += 1

        if issues_criticos > 0:
            return "CRÍTICA - Requiere atención inmediata"
        elif issues_altos > 5:
            return "ALTA - Resolver en próxima iteración"
        elif issues_altos > 0:
            return "MEDIA - Incluir en planificación"
        else:
            return "BAJA - Mejoras opcionales"

    def _generar_recomendaciones_consolidadas(self) -> list:
        """Genera recomendaciones consolidadas de ambas auditorías"""
        recomendaciones = []

        # Recomendaciones de consistencia
        if (
            "consistency" in self.results
            and "recomendaciones" in self.results["consistency"]
        ):
            recomendaciones.extend(self.results["consistency"]["recomendaciones"])

        # Recomendaciones de accesibilidad
        if (
            "accessibility" in self.results
            and "recomendaciones_prioritarias" in self.results["accessibility"]
        ):
            recomendaciones.extend(
                self.results["accessibility"]["recomendaciones_prioritarias"]
            )

        # Recomendaciones adicionales basadas en análisis consolidado
        if len(recomendaciones) > 10:
            recomendaciones.append(
                "📚 Crear documentación de estándares UI/UX para el equipo de desarrollo"
            )

        if any("accesibilidad" in rec.lower() for rec in recomendaciones):
            recomendaciones.append(
                "🎯 Implementar proceso de validación de accesibilidad en CI/CD"
            )

        return recomendaciones

    def _generar_plan_accion(self) -> Dict[str, Any]:
        """Genera un plan de acción priorizado"""
        return {
            "fase_1_critica": [
                "Resolver todos los issues de accesibilidad nivel A críticos",
                "Estandarizar colores y fuentes en módulos principales",
                "Agregar nombres accesibles a todos los elementos interactivos",
            ],
            "fase_2_importante": [
                "Implementar sistema de diseño centralizado",
                "Mejorar contraste de colores para cumplir WCAG AA",
                "Agregar atajos de teclado a funciones principales",
            ],
            "fase_3_mejoras": [
                "Externalizar textos para internacionalización",
                "Optimizar espaciado y márgenes",
                "Implementar tooltips descriptivos",
            ],
            "fase_4_documentacion": [
                "Crear guía de estilo UI/UX",
                "Documentar estándares de accesibilidad",
                "Capacitar al equipo en mejores prácticas",
            ],
        }

    def ejecutar_todas_las_auditorias(self):
        """Ejecuta todas las auditorías UI/UX disponibles"""
        print("🚀 Iniciando auditorías completas de UI/UX...")
        print("=" * 60)

        # Ejecutar auditoría de consistencia
        self.results["consistency"] = self.ejecutar_auditoria_consistencia()

        # Ejecutar auditoría de accesibilidad
        self.results["accessibility"] = self.ejecutar_auditoria_accesibilidad()

        # Generar reporte consolidado
        reporte_path = self.generar_reporte_consolidado()

        # Mostrar resumen final
        self._mostrar_resumen_final()

        return reporte_path

    def _mostrar_resumen_final(self):
        """Muestra un resumen final de todas las auditorías"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL DE AUDITORÍAS UI/UX")
        print("=" * 60)

        # Estadísticas de consistencia
        if (
            "consistency" in self.results
            and "estadisticas" in self.results["consistency"]
        ):
            stats = self.results["consistency"]["estadisticas"]
            print("🎨 Consistencia UI:")
            print(f"   • Issues encontrados: {stats.get('total_issues', 0)}")
            print(f"   • Módulos analizados: {stats.get('modulos_analizados', 0)}")

        # Estadísticas de accesibilidad
        if "accessibility" in self.results:
            acc_result = self.results["accessibility"]
            if "estadisticas" in acc_result:
                stats = acc_result["estadisticas"]
                print("♿ Accesibilidad:")
                print(f"   • Issues encontrados: {stats.get('total_issues', 0)}")
                print(f"   • Score: {acc_result.get('score_accesibilidad', 0)}/100")
                nivel = acc_result.get("nivel_conformidad")
                if nivel:
                    print(f"   • Nivel WCAG: {nivel}")
                else:
                    print("   • Nivel WCAG: No cumple mínimo")

        # Score general
        score_general = self._calcular_score_general()
        print(f"📈 Score general UI/UX: {score_general}/100")

        # Nivel de prioridad
        prioridad = self._determinar_nivel_prioridad()
        print(f"🎯 Prioridad de mejoras: {prioridad}")

        print("\n🎉 Auditorías UI/UX completadas exitosamente!")


def main():
    """Función principal"""
    runner = UIUXAuditRunner()

    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1]

        if comando == "consistency":
            resultado = runner.ejecutar_auditoria_consistencia()
            print(f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")

        elif comando == "accessibility":
            resultado = runner.ejecutar_auditoria_accesibilidad()
            print(f"Resultado: {json.dumps(resultado, indent=2, ensure_ascii=False)}")

        elif comando == "module" and len(sys.argv) > 2:
            modulo = sys.argv[2]
            resultado = runner.analizar_modulo_especifico(modulo)
            print(
                f"Análisis de {modulo}: {json.dumps(resultado, indent=2, ensure_ascii=False)}"
            )

        else:
            print(
                "Uso: python audit_runner.py [consistency|accessibility|module <nombre>]"
            )

    else:
        # Ejecutar todas las auditorías
        reporte_path = runner.ejecutar_todas_las_auditorias()
        print(f"\n📄 Reporte completo disponible en: {reporte_path}")


if __name__ == "__main__":
    main()
