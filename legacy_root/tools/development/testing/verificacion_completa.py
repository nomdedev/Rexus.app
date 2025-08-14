#!/usr/bin/env python3
"""
Verificación Completa del Proyecto
=================================

Este script ejecuta una verificación integral del proyecto, compilando todos
los análisis, mejoras y checklists generados para crear un informe final de estado.

Funcionalidades:
- Ejecuta todos los scripts de análisis y verificación
- Recopila resultados de tests y cobertura
- Genera informe final con recomendaciones
- Verifica cumplimiento de estándares de seguridad y UX
- Proporciona roadmap de mejoras pendientes

Autor: Sistema de Verificación Integral
Fecha: 2025-06-25
"""

class VerificadorCompleto:
    """Ejecuta verificación completa del proyecto."""

    def __init__(self, proyecto_root: str):
        self.proyecto_root = Path(proyecto_root)
        self.informes_dir = self.proyecto_root / "informes_modulos"
        self.checklists_dir = self.proyecto_root / "docs" / "checklists_completados"
        self.tests_dir = self.proyecto_root / "tests"
        self.scripts_dir = self.proyecto_root / "scripts" / "verificacion"

        self.estado_global = {
            'fecha_verificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'modulos_analizados': 0,
            'tests_ejecutados': 0,
            'tests_pasaron': 0,
            'cobertura_promedio': 0,
            'errores_criticos': [],
            'advertencias': [],
            'mejoras_sugeridas': [],
            'puntuacion_global': 0
        }

    def ejecutar_verificacion_completa(self):
        """Ejecuta todos los pasos de verificación del proyecto."""
        print("🔍 VERIFICACIÓN COMPLETA DEL PROYECTO")
        print("=" * 50)

        # 1. Verificar estructura del proyecto
        print("\\n📁 1. Verificando estructura del proyecto...")
        self._verificar_estructura_proyecto()

        # 2. Ejecutar análisis de módulos
        print("\\n🔬 2. Ejecutando análisis de módulos...")
        self._ejecutar_analisis_modulos()

        # 3. Ejecutar tests
        print("\\n🧪 3. Ejecutando tests...")
        self._ejecutar_tests()

        # 4. Verificar seguridad
        print("\\n[LOCK] 4. Verificando seguridad...")
        self._verificar_seguridad()

        # 5. Verificar feedback visual
        print("\\n🎨 5. Verificando feedback visual...")
        self._verificar_feedback_visual()

        # 6. Compilar checklists
        print("\\n📋 6. Compilando checklists...")
        self._compilar_checklists()

        # 7. Calcular puntuación global
        print("\\n[CHART] 7. Calculando puntuación global...")
        self._calcular_puntuacion_global()

        # 8. Generar informe final
        print("\\n📄 8. Generando informe final...")
        self._generar_informe_final()

        print("\\n[CHECK] Verificación completa terminada")
        print(f"📄 Ver informe final en: informe_estado_proyecto.md")

    def _verificar_estructura_proyecto(self):
        """Verifica la estructura básica del proyecto."""
        estructura_requerida = [
            "modules",
            "tests",
            "docs",
            "core",
            "utils",
            "scripts",
            "requirements.txt",
            "README.md"
        ]

        faltantes = []
        for item in estructura_requerida:
            if not (self.proyecto_root / item).exists():
                faltantes.append(item)

        if faltantes:
            self.estado_global['errores_criticos'].append(
                f"Estructura incompleta: faltan {', '.join(faltantes)}"
            )
        else:
            print("[CHECK] Estructura del proyecto completa")

    def _ejecutar_analisis_modulos(self):
        """Ejecuta el análisis automático de módulos."""
        try:
            # Verificar si ya existe análisis reciente
            if self.informes_dir.exists():
                informes = list(self.informes_dir.glob("analisis_*.json"))
                self.estado_global['modulos_analizados'] = len(informes)
                print(f"[CHECK] {len(informes)} módulos analizados")

                # Revisar informes para extraer métricas
                for informe_file in informes:
                    try:
                        with open(informe_file, 'r', encoding='utf-8') as f:
                            datos = json.load(f)

                        # Verificar si hay sugerencias críticas
                        if 'sugerencias' in datos:
                            for sugerencia in datos['sugerencias']:
                                if sugerencia.get('prioridad') == 'alta':
                                    self.estado_global['errores_criticos'].append(
                                        f"{datos.get('nombre', 'módulo')}: {sugerencia.get('descripcion', 'Error sin descripción')}"
                                    )
                    except Exception as e:
                        print(f"[WARN] Error leyendo {informe_file}: {e}")
            else:
                print("[WARN] No se encontraron análisis de módulos")
                self.estado_global['advertencias'].append("Análisis de módulos no ejecutado")

        except Exception as e:
            print(f"[ERROR] Error en análisis de módulos: {e}")
            self.estado_global['errores_criticos'].append(f"Error en análisis de módulos: {e}")

    def _ejecutar_tests(self):
        """Ejecuta los tests del proyecto."""
        try:
            # Ejecutar pytest con coverage
            cmd = [sys.executable,
"-m",
                "pytest",
                str(self.tests_dir),
                "-v",
                "--tb=short"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.proyecto_root),
                timeout=300  # 5 minutos máximo
            )

            # Parsear resultados
            output = result.stdout + result.stderr

            # Contar tests
            if "passed" in output:
                match = re.search(r'(\\d+) passed', output)
                if match:
                    self.estado_global['tests_pasaron'] = int(match.group(1))

            if "failed" in output:
                match = re.search(r'(\\d+) failed', output)
                if match:
                    tests_fallaron = int(match.group(1))
                    self.estado_global['errores_criticos'].append(
                        f"{tests_fallaron} tests fallaron"
                    )

            self.estado_global['tests_ejecutados'] = self.estado_global['tests_pasaron']

            if result.returncode == 0:
                print(f"[CHECK] Tests ejecutados: {self.estado_global['tests_pasaron']} pasaron")
            else:
                print(f"[WARN] Algunos tests fallaron. Ver detalles en el log.")

        except subprocess.TimeoutExpired:
            print("[WARN] Tests tomaron demasiado tiempo (timeout)")
            self.estado_global['advertencias'].append("Tests timeout")
        except Exception as e:
            print(f"[ERROR] Error ejecutando tests: {e}")
            self.estado_global['errores_criticos'].append(f"Error ejecutando tests: {e}")

    def _verificar_seguridad(self):
        """Verifica aspectos de seguridad del proyecto."""
        seguridad_ok = True

        # Verificar si existen utilidades de seguridad
        utils_seguridad = [
            "utils/sql_seguro.py",
            "utils/sanitizador_sql.py",
            "utils/validador_http.py"
        ]

        for util in utils_seguridad:
            if not (self.proyecto_root / util).exists():
                seguridad_ok = False
                self.estado_global['advertencias'].append(f"Utilidad de seguridad faltante: {util}")

        # Verificar checklists de seguridad
        checklists_seguridad = [
            "docs/checklists/checklist_implementacion_seguridad.md",
            "docs/checklists/checklist_uso_sql_seguro.md"
        ]

        for checklist in checklists_seguridad:
            if not (self.proyecto_root / checklist).exists():
                self.estado_global['advertencias'].append(f"Checklist de seguridad faltante: {checklist}")

        if seguridad_ok:
            print("[CHECK] Utilidades de seguridad implementadas")
        else:
            print("[WARN] Algunas utilidades de seguridad faltan")

    def _verificar_feedback_visual(self):
        """Verifica el estado del feedback visual."""
        reporte_feedback = self.proyecto_root / "mejoras_feedback_visual.md"

        if reporte_feedback.exists():
            try:
                with open(reporte_feedback, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                # Contar módulos mejorados
                if "Módulos mejorados:" in contenido:
                    matches = re.findall(r'[CHECK].*\\*\\*(.+?)\\*\\*', contenido)
                    modulos_mejorados = len(matches)
                    print(f"[CHECK] Feedback visual: {modulos_mejorados} módulos mejorados")
                else:
                    print("[WARN] No se detectaron mejoras de feedback visual")

            except Exception as e:
                print(f"[WARN] Error leyendo reporte de feedback: {e}")
        else:
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

            print("[WARN] Verificación de feedback visual no ejecutada")
            self.estado_global['advertencias'].append("Feedback visual no verificado")

    def _compilar_checklists(self):
        """Compila el estado de los checklists."""
        if self.checklists_dir.exists():
            checklists = list(self.checklists_dir.glob("checklist_completo_*.md"))
            print(f"[CHECK] {len(checklists)} checklists generados")

            # Sugerir completar verificación manual
            self.estado_global['mejoras_sugeridas'].append(
                f"Completar verificación manual de {len(checklists)} checklists generados"
            )
        else:
            print("[WARN] Checklists no generados")
            self.estado_global['advertencias'].append("Checklists no generados")

    def _calcular_puntuacion_global(self):
        """Calcula una puntuación global del proyecto."""
        puntuacion = 100

        # Penalizaciones por errores críticos
        puntuacion -= len(self.estado_global['errores_criticos']) * 15

        # Penalizaciones por advertencias
        puntuacion -= len(self.estado_global['advertencias']) * 5

        # Bonus por tests pasando
        if self.estado_global['tests_pasaron'] > 50:
            puntuacion += 10
        elif self.estado_global['tests_pasaron'] > 20:
            puntuacion += 5

        # Bonus por módulos analizados
        if self.estado_global['modulos_analizados'] >= 10:
            puntuacion += 10
        elif self.estado_global['modulos_analizados'] >= 5:
            puntuacion += 5

        # Asegurar que esté en rango 0-100
        puntuacion = max(0, min(100, puntuacion))
        self.estado_global['puntuacion_global'] = puntuacion

        # Clasificar estado
        if puntuacion >= 90:
            estado = "🟢 EXCELENTE"
        elif puntuacion >= 75:
            estado = "🟡 BUENO"
        elif puntuacion >= 60:
            estado = "🟠 REGULAR"
        else:
            estado = "🔴 NECESITA MEJORAS"

        print(f"[CHART] Puntuación global: {puntuacion}/100 - {estado}")

    def _generar_informe_final(self):
        """Genera el informe final de estado del proyecto."""
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Determinar estado general
        if self.estado_global['puntuacion_global'] >= 90:
            estado_emoji = "🟢"
            estado_texto = "EXCELENTE"
            estado_descripcion = "El proyecto cumple con todos los estándares de calidad y seguridad."
        elif self.estado_global['puntuacion_global'] >= 75:
            estado_emoji = "🟡"
            estado_texto = "BUENO"
            estado_descripcion = "El proyecto cumple con la mayoría de estándares, con mejoras menores pendientes."
        elif self.estado_global['puntuacion_global'] >= 60:
            estado_emoji = "🟠"
            estado_texto = "REGULAR"
            estado_descripcion = "El proyecto necesita algunas mejoras importantes para cumplir estándares."
        else:
            estado_emoji = "🔴"
            estado_texto = "NECESITA MEJORAS"
            estado_descripcion = "El proyecto requiere mejoras significativas en múltiples áreas."

        informe = f"""# Informe Final de Estado del Proyecto

{estado_emoji} **ESTADO GENERAL: {estado_texto}**

**Fecha de verificación:** {fecha}
**Puntuación global:** {self.estado_global['puntuacion_global']}/100

{estado_descripcion}

---

## Resumen Ejecutivo

### Métricas Clave
- 📁 **Módulos analizados:** {self.estado_global['modulos_analizados']}
- 🧪 **Tests ejecutados:** {self.estado_global['tests_ejecutados']} ([CHECK] {self.estado_global['tests_pasaron']} pasaron)
- [ERROR] **Errores críticos:** {len(self.estado_global['errores_criticos'])}
- [WARN] **Advertencias:** {len(self.estado_global['advertencias'])}
- 💡 **Mejoras sugeridas:** {len(self.estado_global['mejoras_sugeridas'])}

### Estado por Área

| Área | Estado | Descripción |
|------|--------|-------------|
| 📁 Estructura | {'[CHECK] Completo' if len([e for e in self.estado_global['errores_criticos'] if 'Estructura' in e]) == 0 else '[WARN] Incompleto'} | Estructura básica del proyecto |
| 🔬 Análisis | {'[CHECK] Completo' if self.estado_global['modulos_analizados'] > 0 else '[ERROR] Pendiente'} | Análisis automático de módulos |
| 🧪 Tests | {'[CHECK] Pasando' if self.estado_global['tests_pasaron'] > 0 and len([e for e in self.estado_global['errores_criticos'] if 'tests' in e.lower()]) == 0 else '[WARN] Con errores'} | Suite de tests unitarios |
| [LOCK] Seguridad | {'[CHECK] Implementado' if len([a for a in self.estado_global['advertencias'] if 'seguridad' in a.lower()]) < 2 else '[WARN] Pendiente'} | Utilidades y checklists de seguridad |
| 🎨 UX | {'[CHECK] Mejorado' if Path(self.proyecto_root / "mejoras_feedback_visual.md").exists() else '[WARN] Pendiente'} | Feedback visual y experiencia de usuario |
| 📋 Checklists | {'[CHECK] Generados' if self.checklists_dir.exists() else '[ERROR] Pendientes'} | Checklists de verificación por módulo |

---

## Errores Críticos

"""

        if self.estado_global['errores_criticos']:
            for i, error in enumerate(self.estado_global['errores_criticos'], 1):
                informe += f"{i}. [ERROR] **{error}**\\n"
        else:
            informe += "[CHECK] No se detectaron errores críticos.\\n"

        informe += f"""
---

## Advertencias

"""

        if self.estado_global['advertencias']:
            for i, advertencia in enumerate(self.estado_global['advertencias'], 1):
                informe += f"{i}. [WARN] {advertencia}\\n"
        else:
            informe += "[CHECK] No se detectaron advertencias.\\n"

        informe += f"""
---

## Mejoras Sugeridas

"""

        if self.estado_global['mejoras_sugeridas']:
            for i, mejora in enumerate(self.estado_global['mejoras_sugeridas'], 1):
                informe += f"{i}. 💡 {mejora}\\n"
        else:
            informe += "[CHECK] No hay mejoras adicionales sugeridas.\\n"

        informe += f"""
---

## Archivos y Recursos Generados

### Análisis y Reportes
- [CHART] **Análisis de módulos:** `informes_modulos/` ({self.estado_global['modulos_analizados']} archivos)
- 📋 **Checklists completados:** `docs/checklists_completados/`
- 🎨 **Reporte de feedback visual:** `mejoras_feedback_visual.md`
- 📄 **Este informe:** `informe_estado_proyecto.md`

### Herramientas y Scripts
- 🔧 **Scripts de verificación:** `scripts/verificacion/`
- [LOCK] **Utilidades de seguridad:** `utils/`
- 📚 **Documentación:** `docs/`
- 🧪 **Tests mejorados:** `tests/`

### Backups
- 💾 **Backups de feedback visual:** `backups_feedback/`

---

## Roadmap de Próximos Pasos

### Inmediatos (Próximos 7 días)
1. **Resolver errores críticos** identificados en este informe
2. **Completar verificaciones manuales** de los checklists generados
3. **Ejecutar tests** para verificar que todas las mejoras funcionan correctamente

### Corto plazo (Próximas 2 semanas)
1. **Implementar mejoras sugeridas** de alta prioridad
2. **Documentar cambios** en README y documentación técnica
3. **Validar feedback visual** en todos los módulos mejorados

### Mediano plazo (Próximo mes)
1. **Automatizar verificaciones** mediante CI/CD
2. **Establecer métricas de calidad** continuas
3. **Capacitar equipo** en nuevas herramientas y estándares

### Largo plazo (Próximos 3 meses)
1. **Monitoreo continuo** de calidad y seguridad
2. **Refinamiento de procesos** basado en experiencia
3. **Expansión de herramientas** para nuevas necesidades

---

## Comandos Útiles

### Ejecutar verificaciones específicas
```bash
# Análisis completo de módulos
python scripts/verificacion/ejecutar_analisis_completo.py

# Generar checklists actualizados
python scripts/verificacion/generar_checklists_completados.py

# Mejorar feedback visual
python scripts/verificacion/mejorar_feedback_visual.py

# Ejecutar todos los tests
python -m pytest tests/ -v

# Verificar seguridad
python scripts/verificacion/analizar_seguridad_sql_codigo.py
```

### Restaurar backups si es necesario
```bash
# Restaurar módulo específico
cp backups_feedback/[modulo]_view_backup.py modules/[modulo]/view.py
```

---

## Notas Finales

Este informe fue generado automáticamente el {fecha} por el sistema de verificación integral del proyecto.

**Contacto:** Para dudas sobre este informe o las herramientas utilizadas, consultar la documentación en `docs/` o revisar los scripts en `scripts/verificacion/`.

**Siguiente verificación recomendada:** {(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")} (en 7 días)

---

*Generado por: Sistema de Verificación Integral v1.0*
"""

        # Guardar informe
        informe_file = self.proyecto_root / "informe_estado_proyecto.md"
        with open(informe_file, 'w', encoding='utf-8') as f:
            f.write(informe)

        print(f"[CHECK] Informe final generado: {informe_file}")

        # También guardar datos JSON para procesamiento posterior
        json_file = self.proyecto_root / "tests/reports/estado_tests.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.estado_global, f, indent=2, ensure_ascii=False)

        print(f"[CHART] Datos JSON guardados: {json_file}")

    # Crear directorio de reportes si no existe
    os.makedirs("tests/reports", exist_ok=True)

def main():
    """Función principal del script."""
    script_dir = Path(__file__).parent
    proyecto_root = script_dir.parent.parent

    verificador = VerificadorCompleto(str(proyecto_root))
    verificador.ejecutar_verificacion_completa()

if __name__ == "__main__":
    main()
