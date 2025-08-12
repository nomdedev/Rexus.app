#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para analizar la estructura de cada módulo del proyecto y generar un
informe detallado que sirva como base para la investigación de calidad y seguridad.

Este script:
1. Analiza la estructura de archivos de cada módulo
2. Detecta patrones comunes (MVC, modelos, controladores, vistas)
3. Busca referencias a la base de datos
4. Identifica formularios y widgets de UI
5. Busca patrones de validación de datos
6. Enumera los tests asociados a cada módulo
7. Genera un informe en formato Markdown para cada módulo

Autor: Sistema
Fecha: Generado automáticamente
"""

# Añadir el directorio raíz al path para poder importar módulos del proyecto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root_dir)

# Importar utilidades propias si están disponibles
# Intentar importar AnalisisDB si existe, de lo contrario marcar como no disponible
try:
    analizador_db_mod = importlib.util.find_spec("utils.analizador_db")
    if analizador_db_mod is not None:
        analizador_db_disponible = True
    else:
        analizador_db_disponible = False
except Exception:
    analizador_db_disponible = False
import importlib
import importlib.util
import inspect
import os
import re
import sys
from datetime import datetime

# Configuración
MODULOS_DIR = os.path.join(root_dir, "modules")
TESTS_DIR = os.path.join(root_dir, "tests")
OUTPUT_DIR = os.path.join(root_dir, "docs", "analisis_modulos")
PATRONES_SQL = [
    r"SELECT\s+.*\s+FROM\s+\w+",
    r"INSERT\s+INTO\s+\w+",
    r"UPDATE\s+\w+\s+SET",
    r"DELETE\s+FROM\s+\w+",
    r"EXEC\s+\w+",
    r"EXECUTE\s+\w+",
    r"CREATE\s+TABLE",
    r"ALTER\s+TABLE",
    r"DROP\s+TABLE",
    r"\.execute\(",
    r"cursor\.",
    r"connection\.",
]
PATRONES_VALIDACION = [
    r"validar_",
    r"validate_",
    r"sanitize_",
    r"sanitizar_",
    r"check_input",
    r"verificar_",
    r"is_valid_",
    r"es_valido_",
]
PATRONES_UI_FEEDBACK = [
    r"QMessageBox",
    r"showMessage",
    r"showError",
    r"showWarning",
    r"showInfo",
    r"statusBar",
    r"setEnabled",
    r"setDisabled",
    r"setText",
    r"setStyleSheet",
]

# Estructura para almacenar el análisis de cada módulo
analisis_modulos = {}


def crear_directorio_salida():
    """Crea el directorio de salida si no existe."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Crear archivo índice
    with open(
        os.path.join(OUTPUT_DIR, "00_indice_analisis.md"), "w", encoding="utf-8"
    ) as f:
        f.write("# Índice de Análisis de Módulos\n\n")
        f.write(
            "Este directorio contiene informes de análisis automático para cada módulo del sistema.\n\n"
        )
        f.write("## Módulos Analizados\n\n")
        f.write("| Módulo | Fecha de análisis | Archivos | Tests |\n")
        f.write("|--------|------------------|----------|-------|\n")


def analizar_archivo(ruta_completa):
    """Analiza un archivo Python y devuelve información relevante."""
    info = {
        "tiene_sql": False,
        "consultas_sql": [],
        "tiene_validaciones": False,
        "validaciones": [],
        "tiene_ui_feedback": False,
        "elementos_ui_feedback": [],
        "clases": [],
        "funciones": [],
    }

    try:
        with open(ruta_completa, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar consultas SQL
        for patron in PATRONES_SQL:
            matches = re.findall(patron, contenido, re.IGNORECASE)
            if matches:
                info["tiene_sql"] = True
                info["consultas_sql"].extend(
                    matches[:5]
                )  # Limitar a 5 coincidencias por patrón

        # Buscar validaciones
        for patron in PATRONES_VALIDACION:
            matches = re.findall(patron + r"\w+", contenido, re.IGNORECASE)
            if matches:
                info["tiene_validaciones"] = True
                info["validaciones"].extend(
                    matches[:5]
                )  # Limitar a 5 coincidencias por patrón

        # Buscar UI Feedback
        for patron in PATRONES_UI_FEEDBACK:
            matches = re.findall(patron + r".*", contenido, re.IGNORECASE)
            if matches:
                info["tiene_ui_feedback"] = True
                info["elementos_ui_feedback"].extend(
                    matches[:5]
                )  # Limitar a 5 coincidencias por patrón

        # Intentar extraer clases y funciones
        try:
            spec = importlib.util.spec_from_file_location("module.name", ruta_completa)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Extraer clases
                for nombre, obj in inspect.getmembers(module, inspect.isclass):
                    if (
                        obj.__module__ == "module.name"
                    ):  # Solo clases definidas en este módulo
                        info["clases"].append(nombre)

                # Extraer funciones
                for nombre, obj in inspect.getmembers(module, inspect.isfunction):
                    if (
                        obj.__module__ == "module.name"
                    ):  # Solo funciones definidas en este módulo
                        info["funciones"].append(nombre)
        except Exception as e:
            # Falló la importación dinámica, intentar extraer mediante expresiones regulares
            class_matches = re.findall(r"class\s+(\w+)(?:\([\w\.,\s]*\))?:", contenido)
            info["clases"].extend(class_matches)

            func_matches = re.findall(r"def\s+(\w+)\s*\(", contenido)
            info["funciones"].extend(func_matches)

    except Exception as e:
        print(f"Error al analizar archivo {ruta_completa}: {e}")

    return info


def analizar_modulo(nombre_modulo):
    """Analiza la estructura completa de un módulo."""
    ruta_modulo = os.path.join(MODULOS_DIR, nombre_modulo)
    if not os.path.exists(ruta_modulo):
        return None

    info_modulo = {
        "nombre": nombre_modulo,
        "archivos": [],
        "tests": [],
        "modelo_detectado": False,
        "vista_detectada": False,
        "controlador_detectado": False,
        "tiene_db_conexion": False,
        "tiene_formularios": False,
        "tiene_validaciones": False,
        "tiene_tests": False,
        "estructura_mvc": False,
        "archivos_por_tipo": {
            "modelo": [],
            "vista": [],
            "controlador": [],
            "ui": [],
            "utils": [],
            "config": [],
            "otro": [],
        },
    }

    # Analizar estructura de archivos del módulo
    for root, dirs, files in os.walk(ruta_modulo):
        for file in files:
            if file.endswith(".py"):
                ruta_completa = os.path.join(root, file)
                ruta_relativa = os.path.relpath(ruta_completa, MODULOS_DIR)

                info_archivo = {
                    "nombre": file,
                    "ruta": ruta_relativa,
                    "tipo": "otro",
                    "analisis": analizar_archivo(ruta_completa),
                }

                # Detectar tipo de archivo
                if "model" in file.lower():
                    info_archivo["tipo"] = "modelo"
                    info_modulo["modelo_detectado"] = True
                    info_modulo["archivos_por_tipo"]["modelo"].append(ruta_relativa)
                elif "view" in file.lower() or "ui" in file.lower():
                    info_archivo["tipo"] = "vista"
                    info_modulo["vista_detectada"] = True
                    info_modulo["archivos_por_tipo"]["vista"].append(ruta_relativa)
                elif "controller" in file.lower() or "ctrl" in file.lower():
                    info_archivo["tipo"] = "controlador"
                    info_modulo["controlador_detectado"] = True
                    info_modulo["archivos_por_tipo"]["controlador"].append(
                        ruta_relativa
                    )
                elif "form" in file.lower() or "widget" in file.lower():
                    info_archivo["tipo"] = "ui"
                    info_modulo["tiene_formularios"] = True
                    info_modulo["archivos_por_tipo"]["ui"].append(ruta_relativa)
                elif "util" in file.lower() or "helper" in file.lower():
                    info_archivo["tipo"] = "utils"
                    info_modulo["archivos_por_tipo"]["utils"].append(ruta_relativa)
                elif "config" in file.lower() or "settings" in file.lower():
                    info_archivo["tipo"] = "config"
                    info_modulo["archivos_por_tipo"]["config"].append(ruta_relativa)
                else:
                    info_modulo["archivos_por_tipo"]["otro"].append(ruta_relativa)

                # Verificar uso de base de datos
                if info_archivo["analisis"]["tiene_sql"]:
                    info_modulo["tiene_db_conexion"] = True

                # Verificar validaciones
                if info_archivo["analisis"]["tiene_validaciones"]:
                    info_modulo["tiene_validaciones"] = True

                info_modulo["archivos"].append(info_archivo)

    # Buscar tests asociados al módulo
    ruta_tests_modulo = os.path.join(TESTS_DIR, nombre_modulo)
    if os.path.exists(ruta_tests_modulo):
        info_modulo["tiene_tests"] = True
        for root, dirs, files in os.walk(ruta_tests_modulo):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    ruta_completa = os.path.join(root, file)
                    ruta_relativa = os.path.relpath(ruta_completa, TESTS_DIR)
                    info_modulo["tests"].append(ruta_relativa)

    # Determinar si sigue estructura MVC
    info_modulo["estructura_mvc"] = (
        info_modulo["modelo_detectado"]
        and info_modulo["vista_detectada"]
        and info_modulo["controlador_detectado"]
    )

    return info_modulo


def generar_informe_modulo(info_modulo):
    """Genera un informe detallado en formato Markdown para un módulo."""
    if not info_modulo:
        return

    nombre_modulo = info_modulo["nombre"]
    ruta_informe = os.path.join(OUTPUT_DIR, f"{nombre_modulo}_analisis.md")

    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write(f"# Análisis del Módulo: {nombre_modulo}\n\n")
        f.write(
            f"*Informe generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        )

        f.write("## Resumen\n\n")
        f.write(
            f"- **Estructura MVC**: {'Sí' if info_modulo['estructura_mvc'] else 'No'}\n"
        )
        f.write(
            f"- **Modelo detectado**: {'Sí' if info_modulo['modelo_detectado'] else 'No'}\n"
        )
        f.write(
            f"- **Vista detectada**: {'Sí' if info_modulo['vista_detectada'] else 'No'}\n"
        )
        f.write(
            f"- **Controlador detectado**: {'Sí' if info_modulo['controlador_detectado'] else 'No'}\n"
        )
        f.write(
            f"- **Conexión a base de datos**: {'Sí' if info_modulo['tiene_db_conexion'] else 'No'}\n"
        )
        f.write(
            f"- **Formularios UI**: {'Sí' if info_modulo['tiene_formularios'] else 'No'}\n"
        )
        f.write(
            f"- **Validaciones**: {'Sí' if info_modulo['tiene_validaciones'] else 'No'}\n"
        )
        f.write(f"- **Tests**: {'Sí' if info_modulo['tiene_tests'] else 'No'}\n")
        f.write(f"- **Total de archivos**: {len(info_modulo['archivos'])}\n")
        f.write(f"- **Total de tests**: {len(info_modulo['tests'])}\n\n")

        f.write("## Estructura de Archivos\n\n")

        # Mostrar archivos por tipo
        for tipo, archivos in info_modulo["archivos_por_tipo"].items():
            if archivos:
                f.write(f"### {tipo.capitalize()}\n\n")
                for archivo in archivos:
                    f.write(f"- `{archivo}`\n")
                f.write("\n")

        # Mostrar tests
        if info_modulo["tests"]:
            f.write("### Tests\n\n")
            for test in info_modulo["tests"]:
                f.write(f"- `{test}`\n")
            f.write("\n")

        # Detalles de archivos
        f.write("## Análisis Detallado de Archivos\n\n")
        for archivo in info_modulo["archivos"]:
            f.write(f"### {archivo['nombre']}\n\n")
            f.write(f"- **Tipo**: {archivo['tipo']}\n")
            f.write(f"- **Ruta**: `{archivo['ruta']}`\n")

            analisis = archivo["analisis"]

            # Clases y funciones
            if analisis["clases"]:
                f.write("\n**Clases:**\n\n")
                for clase in analisis["clases"]:
                    f.write(f"- `{clase}`\n")

            if analisis["funciones"]:
                f.write("\n**Funciones:**\n\n")
                for funcion in analisis["funciones"]:
                    f.write(f"- `{funcion}`\n")

            # SQL
            if analisis["tiene_sql"]:
                f.write("\n**Consultas SQL detectadas:**\n\n")
                for sql in analisis["consultas_sql"]:
                    sql_clean = sql.replace("\n", " ").strip()
                    if len(sql_clean) > 100:
                        sql_clean = sql_clean[:100] + "..."
                    f.write(f"- `{sql_clean}`\n")

            # Validaciones
            if analisis["tiene_validaciones"]:
                f.write("\n**Validaciones detectadas:**\n\n")
                for validacion in analisis["validaciones"]:
                    f.write(f"- `{validacion}`\n")

            # UI Feedback
            if analisis["tiene_ui_feedback"]:
                f.write("\n**Elementos de feedback visual:**\n\n")
                for elemento in analisis["elementos_ui_feedback"]:
                    elemento_clean = elemento.replace("\n", " ").strip()
                    if len(elemento_clean) > 100:
                        elemento_clean = elemento_clean[:100] + "..."
                    f.write(f"- `{elemento_clean}`\n")

            f.write("\n---\n\n")

        f.write("## Recomendaciones Preliminares\n\n")

        # Generar recomendaciones basadas en el análisis
        recomendaciones = []

        if not info_modulo["estructura_mvc"]:
            recomendaciones.append(
                "- Considerar implementar una estructura MVC más clara para mejorar la organización del código."
            )

        if info_modulo["tiene_db_conexion"] and not info_modulo["tiene_validaciones"]:
            recomendaciones.append(
                "- Añadir validaciones de datos en los archivos que interactúan con la base de datos."
            )

        if not info_modulo["tiene_tests"]:
            recomendaciones.append("- Crear tests unitarios para el módulo.")
        elif len(info_modulo["tests"]) < len(info_modulo["archivos"]) / 2:
            recomendaciones.append(
                "- Aumentar la cobertura de tests. Actualmente hay menos tests que archivos en el módulo."
            )

        if not info_modulo["tiene_validaciones"] and info_modulo["tiene_formularios"]:
            recomendaciones.append(
                "- Implementar validación de entradas en los formularios UI."
            )

        if not recomendaciones:
            recomendaciones.append(
                "- El módulo parece estar bien estructurado según el análisis automático."
            )

        for recomendacion in recomendaciones:
            f.write(f"{recomendacion}\n")

        f.write("\n## Próximos Pasos\n\n")
        f.write(
            "1. Revisar manualmente los archivos clave identificados en este análisis\n"
        )
        f.write(
            "2. Verificar la correcta implementación del feedback visual para el usuario\n"
        )
        f.write(
            "3. Comprobar que todas las interacciones con la base de datos utilizan las utilidades de seguridad SQL\n"
        )
        f.write("4. Revisar la cobertura de tests y añadir edge cases\n")

    print(f"Informe generado para el módulo '{nombre_modulo}' en {ruta_informe}")
    return ruta_informe


def actualizar_indice(informes_generados):
    """Actualiza el archivo índice con los informes generados."""
    ruta_indice = os.path.join(OUTPUT_DIR, "00_indice_analisis.md")

    with open(ruta_indice, "w", encoding="utf-8") as f:
        f.write("# Índice de Análisis de Módulos\n\n")
        f.write(
            "Este directorio contiene informes de análisis automático para cada módulo del sistema.\n\n"
        )
        f.write("## Módulos Analizados\n\n")
        f.write("| Módulo | Fecha de análisis | Archivos | Tests |\n")
        f.write("|--------|------------------|----------|-------|\n")

        for modulo, info in analisis_modulos.items():
            fecha = datetime.now().strftime("%Y-%m-%d")
            num_archivos = len(info["archivos"])
            num_tests = len(info["tests"])

            f.write(
                f"| [{modulo}]({modulo}_analisis.md) | {fecha} | {num_archivos} | {num_tests} |\n"
            )

        f.write("\n## Cómo usar estos análisis\n\n")
        f.write(
            "Estos informes son una primera aproximación automática para facilitar el análisis manual más profundo.\n"
        )
        f.write("Recomendamos usarlos como punto de partida para:\n\n")
        f.write("1. Identificar los archivos más relevantes de cada módulo\n")
        f.write("2. Detectar patrones de uso de SQL y validaciones\n")
        f.write("3. Evaluar la estructura general y la cobertura de tests\n")
        f.write("4. Priorizar las áreas que requieren más atención\n\n")
        f.write(
            "Los informes completos contienen recomendaciones preliminares basadas en el análisis automático.\n"
        )


def generar_checklist_especifico_modulo(nombre_modulo, info_modulo):
    """Genera un checklist específico para un módulo basado en su análisis."""
    ruta_checklist = os.path.join(
        root_dir, "docs", "checklists", f"verificacion_{nombre_modulo}.md"
    )

    with open(ruta_checklist, "w", encoding="utf-8") as f:
        f.write(f"# Checklist de Verificación: Módulo {nombre_modulo}\n\n")
        f.write(
            f"*Generado automáticamente el {datetime.now().strftime('%Y-%m-%d')} basado en análisis estructural*\n\n"
        )

        f.write("## Objetivo\n\n")
        f.write(
            "Este checklist personalizado guía la verificación exhaustiva de las funcionalidades, interfaz de usuario, "
        )
        f.write(
            "seguridad y tests del módulo, con énfasis en las áreas identificadas en el análisis automático.\n\n"
        )

        # Sección de UI y carga de datos, adaptada al tipo de módulo
        f.write("## 1. Revisión de UI y Carga de Datos\n\n")

        # Identificar vistas y formularios específicos
        vistas = info_modulo["archivos_por_tipo"]["vista"]
        ui_forms = info_modulo["archivos_por_tipo"]["ui"]

        if vistas or ui_forms:
            f.write("### Formularios y vistas detectados\n\n")

            elementos_ui = vistas + ui_forms
            for elem in elementos_ui:
                nombre_simple = os.path.basename(elem).replace(".py", "")
                f.write(f"- [ ] **{nombre_simple}**\n")
                f.write(
                    f"  - [ ] Verificar que todos los elementos visuales se cargan correctamente\n"
                )
                f.write(
                    f"  - [ ] Comprobar que los datos iniciales se muestran correctamente\n"
                )
                f.write(
                    f"  - [ ] Validar comportamiento con diferentes tipos de entrada\n"
                )
                f.write(f"  - [ ] Verificar responsive y escalado de elementos UI\n\n")
        else:
            f.write(
                "*No se detectaron archivos de UI específicos. Verificar si este módulo tiene interfaz visual.*\n\n"
            )

        # Sección de feedback visual
        f.write("## 2. Feedback Visual\n\n")

        # Buscar elementos de UI con feedback en el análisis
        tiene_feedback = False
        for archivo in info_modulo["archivos"]:
            if archivo["analisis"]["tiene_ui_feedback"]:
                tiene_feedback = True
                break

        if tiene_feedback:
            f.write("### Operaciones con feedback visual detectadas\n\n")
            f.write("- [ ] **Operaciones de creación/guardado**\n")
            f.write(
                "  - [ ] Verificar indicadores de progreso durante operaciones largas\n"
            )
            f.write(
                "  - [ ] Comprobar mensajes de éxito/error tras completar operaciones\n"
            )
            f.write(
                "  - [ ] Validar feedback visual en formularios (colores, iconos, etc.)\n\n"
            )
            f.write("- [ ] **Operaciones de eliminación/modificación**\n")
            f.write(
                "  - [ ] Verificar mensajes de confirmación antes de acciones destructivas\n"
            )
            f.write(
                "  - [ ] Comprobar indicación clara del resultado tras la acción\n\n"
            )
            f.write("- [ ] **Errores y excepciones**\n")
            f.write("  - [ ] Verificar que los mensajes de error son claros y útiles\n")
            f.write(
                "  - [ ] Comprobar que la UI se recupera adecuadamente tras errores\n\n"
            )
        else:
            f.write(
                "*No se detectaron elementos explícitos de feedback visual. Verificar si son necesarios para la funcionalidad del módulo.*\n\n"
            )

        # Sección de seguridad en base de datos
        f.write("## 3. Verificación de Operaciones con Base de Datos\n\n")

        # Analizar si hay operaciones SQL
        if info_modulo["tiene_db_conexion"]:
            f.write("### Operaciones SQL detectadas\n\n")
            f.write("- [ ] **Consultas SELECT**\n")
            f.write(
                "  - [ ] Verificar uso de parámetros preparados o funciones de escape\n"
            )
            f.write("  - [ ] Comprobar validación de parámetros de entrada\n")
            f.write(
                "  - [ ] Validar uso de utils.sql_seguro para construcción de queries\n\n"
            )
            f.write("- [ ] **Operaciones de inserción/actualización**\n")
            f.write("  - [ ] Verificar validación de datos antes de guardar\n")
            f.write("  - [ ] Comprobar manejo adecuado de transacciones\n")
            f.write("  - [ ] Validar que los datos se guardan correctamente\n\n")
            f.write("- [ ] **Operaciones de eliminación**\n")
            f.write("  - [ ] Verificar confirmaciones antes de eliminar\n")
            f.write(
                "  - [ ] Comprobar eliminación lógica vs física según corresponda\n\n"
            )
        else:
            f.write(
                "*No se detectaron operaciones directas con base de datos. Verificar si el módulo usa servicios o modelos externos para acceso a datos.*\n\n"
            )

        # Sección de análisis de tests
        f.write("## 4. Análisis de Tests\n\n")

        if info_modulo["tiene_tests"]:
            f.write("### Tests existentes\n\n")
            for test in info_modulo["tests"]:
                test_name = os.path.basename(test)
                f.write(f"- [ ] **{test_name}**\n")
                f.write(f"  - [ ] Verificar cobertura de funcionalidades principales\n")
                f.write(f"  - [ ] Comprobar casos de borde/edge cases\n")
                f.write(f"  - [ ] Validar tests de errores y excepciones\n\n")

            f.write("### Edge cases a añadir\n\n")
            f.write("- [ ] Tests de entrada con caracteres especiales/peligrosos\n")
            f.write("- [ ] Tests de concurrencia/situaciones de carrera\n")
            f.write("- [ ] Tests de validación de permisos/acceso\n")
            f.write(
                "- [ ] Tests de comportamiento con datos extremos (muy grandes, muy pequeños, nulos)\n\n"
            )
        else:
            f.write(
                "*No se detectaron tests para este módulo. Considerar crear tests unitarios y de integración prioritariamente.*\n\n"
            )
            f.write("### Tests sugeridos a implementar\n\n")
            f.write("- [ ] Tests de funcionalidades básicas CRUD\n")
            f.write("- [ ] Tests de validación de entradas\n")
            f.write("- [ ] Tests de manejo de errores\n")
            f.write("- [ ] Tests de integración con otros módulos\n\n")

        # Sección de recomendaciones
        f.write("## 5. Recomendaciones Específicas\n\n")

        if not info_modulo["estructura_mvc"]:
            f.write(
                "- [ ] **Estructura**: Considerar refactorización a patrón MVC más claro\n"
            )

        if info_modulo["tiene_db_conexion"] and not info_modulo["tiene_validaciones"]:
            f.write(
                "- [ ] **Seguridad**: Implementar validaciones estrictas para todas las entradas antes de operaciones SQL\n"
            )

        if not info_modulo["tiene_tests"]:
            f.write(
                "- [ ] **Tests**: Priorizar creación de tests unitarios para funcionalidades críticas\n"
            )

        f.write("\n## 6. Tabla de Registro de Revisión\n\n")
        f.write("| Funcionalidad | Revisado por | Fecha | Estado | Observaciones |\n")
        f.write("|--------------|--------------|-------|--------|---------------|\n")
        f.write("| | | | | |\n")
        f.write("| | | | | |\n")
        f.write("| | | | | |\n\n")

        f.write("## 7. Siguientes Pasos\n\n")
        f.write(
            "1. Completar la revisión de todos los componentes usando este checklist\n"
        )
        f.write("2. Documentar hallazgos y problemas detectados\n")
        f.write(
            "3. Implementar mejoras priorizando seguridad y experiencia de usuario\n"
        )
        f.write("4. Actualizar tests según hallazgos\n")
        f.write("5. Validar implementación con otro desarrollador\n")

    print(
        f"Checklist específico generado para el módulo '{nombre_modulo}' en {ruta_checklist}"
    )
    return ruta_checklist


def crear_informe_resumen(modulos_analizados):
    """Crea un informe resumen de todos los módulos analizados."""
    ruta_resumen = os.path.join(OUTPUT_DIR, "resumen_analisis.md")

    with open(ruta_resumen, "w", encoding="utf-8") as f:
        f.write("# Resumen de Análisis de Módulos\n\n")
        f.write(f"*Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")

        f.write("## Estadísticas Generales\n\n")

        total_archivos = sum(
            len(info["archivos"]) for info in analisis_modulos.values()
        )
        total_tests = sum(len(info["tests"]) for info in analisis_modulos.values())

        modulos_con_mvc = sum(
            1 for info in analisis_modulos.values() if info["estructura_mvc"]
        )
        modulos_con_db = sum(
            1 for info in analisis_modulos.values() if info["tiene_db_conexion"]
        )
        modulos_con_tests = sum(
            1 for info in analisis_modulos.values() if info["tiene_tests"]
        )
        modulos_con_validaciones = sum(
            1 for info in analisis_modulos.values() if info["tiene_validaciones"]
        )

        f.write(f"- **Total de módulos analizados**: {len(modulos_analizados)}\n")
        f.write(f"- **Total de archivos Python**: {total_archivos}\n")
        f.write(f"- **Total de archivos de test**: {total_tests}\n")
        f.write(
            f"- **Módulos con estructura MVC**: {modulos_con_mvc} ({modulos_con_mvc/len(modulos_analizados)*100:.1f}%)\n"
        )
        f.write(
            f"- **Módulos con conexión a BD**: {modulos_con_db} ({modulos_con_db/len(modulos_analizados)*100:.1f}%)\n"
        )
        f.write(
            f"- **Módulos con tests**: {modulos_con_tests} ({modulos_con_tests/len(modulos_analizados)*100:.1f}%)\n"
        )
        f.write(
            f"- **Módulos con validaciones**: {modulos_con_validaciones} ({modulos_con_validaciones/len(modulos_analizados)*100:.1f}%)\n\n"
        )

        f.write("## Resumen por Módulo\n\n")
        f.write(
            "| Módulo | Archivos | Tests | MVC | BD | Validaciones | Prioridad de revisión |\n"
        )
        f.write(
            "|--------|----------|-------|-----|----|--------------|-----------------------|\n"
        )

        # Calcular prioridad para cada módulo
        for nombre, info in analisis_modulos.items():
            score = 0

            # Si tiene BD pero no validaciones, alta prioridad
            if info["tiene_db_conexion"] and not info["tiene_validaciones"]:
                score += 3

            # Si no tiene tests, media prioridad
            if not info["tiene_tests"]:
                score += 2
            elif len(info["tests"]) < len(info["archivos"]) / 3:  # Pocos tests
                score += 1

            prioridad = "Alta" if score >= 3 else "Media" if score >= 1 else "Baja"

            f.write(
                f"| [{nombre}]({nombre}_analisis.md) | {len(info['archivos'])} | {len(info['tests'])} | "
            )
            f.write(f"{'[OK]' if info['estructura_mvc'] else '✗'} | ")
            f.write(f"{'[OK]' if info['tiene_db_conexion'] else '✗'} | ")
            f.write(f"{'[OK]' if info['tiene_validaciones'] else '✗'} | ")
            f.write(f"{prioridad} |\n")

        f.write("\n## Recomendaciones Generales\n\n")

        # Generar recomendaciones generales basadas en los hallazgos
        recomendaciones = []

        if modulos_con_mvc < len(modulos_analizados) * 0.7:
            recomendaciones.append(
                "- **Estandarizar estructura MVC**: Varios módulos carecen de una estructura MVC clara. Considerar una refactorización para mejorar la mantenibilidad."
            )

        if modulos_con_db > modulos_con_validaciones:
            recomendaciones.append(
                "- **Reforzar validaciones de datos**: Existen módulos que acceden a la base de datos sin validaciones adecuadas. Implementar validaciones robustas para todas las entradas."
            )

        if modulos_con_tests < len(modulos_analizados) * 0.8:
            recomendaciones.append(
                "- **Aumentar cobertura de tests**: Varios módulos carecen de tests o tienen cobertura insuficiente. Priorizar la creación de tests unitarios para funcionalidades críticas."
            )

        for recomendacion in recomendaciones:
            f.write(f"{recomendacion}\n")

        f.write("\n## Plan de Acción Sugerido\n\n")
        f.write("1. **Corto plazo** (1-2 semanas):\n")
        f.write(
            "   - Completar checklists de verificación para módulos de prioridad Alta\n"
        )
        f.write(
            "   - Implementar validaciones para módulos con acceso a BD sin validaciones\n"
        )
        f.write(
            "   - Crear tests básicos para funcionalidades críticas sin cobertura\n\n"
        )

        f.write("2. **Medio plazo** (2-4 semanas):\n")
        f.write("   - Completar checklists para módulos de prioridad Media\n")
        f.write(
            "   - Refactorizar para mejorar estructura MVC en módulos prioritarios\n"
        )
        f.write(
            "   - Ampliar cobertura de tests con edge cases y pruebas de integración\n\n"
        )

        f.write("3. **Largo plazo** (1-2 meses):\n")
        f.write("   - Completar todos los checklists restantes\n")
        f.write("   - Estandarizar estructura y patrones en todos los módulos\n")
        f.write("   - Implementar pruebas automatizadas de UI y sistema completo\n")

    print(f"Informe resumen generado en {ruta_resumen}")
    return ruta_resumen


def main():
    """Función principal."""
    print("Analizando estructura de módulos...")

    # Crear directorio de salida
    crear_directorio_salida()

    # Obtener lista de módulos
    modulos = [
        d
        for d in os.listdir(MODULOS_DIR)
        if os.path.isdir(os.path.join(MODULOS_DIR, d))
    ]

    # Analizar cada módulo
    for modulo in modulos:
        print(f"Analizando módulo: {modulo}")
        info_modulo = analizar_modulo(modulo)
        if info_modulo:
            analisis_modulos[modulo] = info_modulo
            generar_informe_modulo(info_modulo)
            generar_checklist_especifico_modulo(modulo, info_modulo)

    # Actualizar índice
    actualizar_indice(analisis_modulos)

    # Crear informe resumen
    crear_informe_resumen(modulos)

    print(f"\nAnálisis completado. Se analizaron {len(analisis_modulos)} módulos.")
    print(f"Los informes se han guardado en {OUTPUT_DIR}")
    print(
        f"Los checklists específicos se han guardado en {os.path.join(root_dir, 'docs', 'checklists')}"
    )


if __name__ == "__main__":
    main()
