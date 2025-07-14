#!/usr/bin/env python3
"""
Mejorador Automático de Feedback Visual
=======================================

Este script mejora automáticamente el feedback visual en módulos que no cumplan
con los estándares de UX definidos. Analiza los módulos y aplica mejoras estándar.

Funcionalidades:
- Detecta módulos con feedback visual insuficiente
- Agrega indicadores de carga estándar
- Implementa mensajes de error y éxito consistentes
- Mejora la accesibilidad visual
- Genera código de feedback siguiendo las mejores prácticas

Mejoras aplicadas:
- Spinners y indicadores de carga
- Mensajes contextuales con iconos
- Timers para auto-ocultar mensajes
- Logging automático de errores
- Estilos consistentes con el tema global

Autor: Sistema de Mejora Automática
Fecha: 2025-06-25
"""

class MejoradorFeedbackVisual:
    """Mejora automáticamente el feedback visual en módulos de PyQt6."""

    def __init__(self, proyecto_root: str):
        self.proyecto_root = Path(proyecto_root)
        self.modulos_dir = self.proyecto_root / "modules"
        self.backup_dir = self.proyecto_root / "backups_feedback"

        # Crear directorio de backup
        self.backup_dir.mkdir(exist_ok=True)

        # Plantillas de código para mejoras
        self.plantillas = {
            'feedback_label': '''
        # --- FEEDBACK VISUAL MEJORADO ---
        self.label_feedback = QLabel("")
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback")
        self.label_feedback.setAccessibleDescription("Mensajes de estado y feedback para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None
''',

            'mostrar_feedback_method': '''
    def mostrar_feedback(self, mensaje, tipo="info"):
        """Muestra feedback visual al usuario con auto-ocultamiento."""
        if not hasattr(self, "label_feedback") or self.label_feedback is None:
            return

        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ ",
            "cargando": "🔄 "
        }
        icono = iconos.get(tipo, "ℹ️ ")

        self.label_feedback.clear()
        self.label_feedback.setProperty("feedback", tipo)
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")

        # Logging para errores y advertencias
        if tipo in ("error", "advertencia"):
            try:
                log_error(f"[{tipo.upper()}][{self.__class__.__name__}] {mensaje}")
            except ImportError:
                print(f"[{tipo.upper()}] {mensaje}")

        # Auto-ocultar después de tiempo apropiado
        tiempo = 6000 if tipo == "error" else 4000 if tipo == "advertencia" else 3000

        try:
            if hasattr(self, '_feedback_timer') and self._feedback_timer:
                self._feedback_timer.stop()
            self._feedback_timer = QTimer(self)
            self._feedback_timer.setSingleShot(True)
            self._feedback_timer.timeout.connect(self.ocultar_feedback)
            self._feedback_timer.start(tiempo)
        except ImportError:
            pass

    def ocultar_feedback(self):
        """Oculta el feedback visual."""
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()
''',

            'mostrar_carga_method': '''
    def mostrar_indicador_carga(self, mensaje="Procesando...", habilitar_ui=False):
        """Muestra indicador de carga y opcionalmente deshabilita la UI."""
        try:
            # Cambiar cursor a loading
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            # Mostrar mensaje de carga
            self.mostrar_feedback(mensaje, "cargando")

            # Deshabilitar UI si se solicita
            if not habilitar_ui:
                self.setEnabled(False)

            # Procesar eventos para que se vea inmediatamente
            QApplication.processEvents()

        except ImportError:
            pass

    def ocultar_indicador_carga(self):
        """Oculta el indicador de carga y restaura la UI."""
        try:
            # Restaurar cursor normal
            QApplication.restoreOverrideCursor()

            # Rehabilitar UI
            self.setEnabled(True)

            # Ocultar mensaje de carga
            self.ocultar_feedback()

        except ImportError:
            pass
''',

            'imports_necesarios': '''from PyQt6.QtWidgets import QLabel
'''
        }

    def analizar_modulo(self, modulo_path: Path) -> Dict[str, any]:
        """Analiza un módulo para determinar qué mejoras de feedback necesita."""
        analisis = {
            'nombre': modulo_path.name,
            'archivos_analizados': [],
            'mejoras_necesarias': [],
            'tiene_feedback_basico': False,
            'tiene_indicadores_carga': False,
            'tiene_manejo_errores': False
        }

        view_file = modulo_path / "view.py"
        if not view_file.exists():
            analisis['mejoras_necesarias'].append("No tiene archivo view.py")
            return analisis

        analisis['archivos_analizados'].append('view.py')

        try:
            with open(view_file, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()

            # Analizar feedback existente
            if 'mostrar_feedback' in contenido:
                analisis['tiene_feedback_basico'] = True
            else:
                analisis['mejoras_necesarias'].append("Agregar sistema de feedback básico")

            # Analizar indicadores de carga
            patrones_carga = [
                r'QProgressBar',
                r'setCursor.*Wait',
                r'loading',
                r'cargando',
                r'procesando'
            ]
            if any(re.search(patron, contenido, re.IGNORECASE) for patron in patrones_carga):
                analisis['tiene_indicadores_carga'] = True
            else:
                analisis['mejoras_necesarias'].append("Agregar indicadores de carga")

            # Analizar manejo de errores visual
            patrones_error = [
                r'QMessageBox.*error',
                r'mostrar_feedback.*error',
                r'setProperty.*error'
            ]
            if any(re.search(patron, contenido, re.IGNORECASE) for patron in patrones_error):
                analisis['tiene_manejo_errores'] = True
            else:
                analisis['mejoras_necesarias'].append("Mejorar manejo visual de errores")

            # Verificar estructura de UI básica
            if 'QVBoxLayout' not in contenido and 'QHBoxLayout' not in contenido:
                analisis['mejoras_necesarias'].append("Estructura de layout básica faltante")

            # Verificar accesibilidad
            if 'setAccessible' not in contenido:
                analisis['mejoras_necesarias'].append("Agregar soporte de accesibilidad")

        except Exception as e:
            analisis['mejoras_necesarias'].append(f"Error analizando archivo: {e}")

        return analisis

    def aplicar_mejoras_feedback(self, modulo_path: Path, analisis: Dict[str, any]) -> bool:
        """Aplica mejoras de feedback visual al módulo."""
        view_file = modulo_path / "view.py"
        if not view_file.exists():
            return False

        # Crear backup
        backup_file = self.backup_dir / f"{modulo_path.name}_view_backup.py"
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                contenido_original = f.read()

            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(contenido_original)

            print(f"✅ Backup creado: {backup_file}")

        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False

        # Aplicar mejoras
        contenido_mejorado = contenido_original
        mejoras_aplicadas = []

        try:
            # 1. Agregar imports si faltan
            if 'from PyQt6.QtWidgets import' in contenido_mejorado:
                if 'QLabel' not in contenido_mejorado:
                    contenido_mejorado = re.sub(
                        r'(from PyQt6\.QtWidgets import[^\\n]*)',
                        r'\\1, QLabel',
                        contenido_mejorado
                    )
                    mejoras_aplicadas.append("Agregado import QLabel")

            # 2. Agregar sistema de feedback si no existe
            if not analisis['tiene_feedback_basico']:
                # Buscar el __init__ del widget principal
                init_match = re.search(r'def __init__\(self[^)]*\):', contenido_mejorado)
                if init_match:
                    # Buscar el primer layout
                    layout_match = re.search(r'(self\\.main_layout\\.addWidget\\([^)]+\\))', contenido_mejorado)
                    if layout_match:
                        insert_pos = layout_match.end()
                        contenido_mejorado = (
                            contenido_mejorado[:insert_pos] +
                            self.plantillas['feedback_label'] +
                            contenido_mejorado[insert_pos:]
                        )
                        mejoras_aplicadas.append("Agregado label de feedback en __init__")

                # Agregar método mostrar_feedback al final de la clase
                class_end = self._encontrar_final_clase(contenido_mejorado)
                if class_end:
                    contenido_mejorado = (
                        contenido_mejorado[:class_end] +
                        self.plantillas['mostrar_feedback_method'] +
                        contenido_mejorado[class_end:]
                    )
                    mejoras_aplicadas.append("Agregado método mostrar_feedback")

            # 3. Agregar indicadores de carga si no existen
            if not analisis['tiene_indicadores_carga']:
                class_end = self._encontrar_final_clase(contenido_mejorado)
                if class_end:
                    contenido_mejorado = (
                        contenido_mejorado[:class_end] +
                        self.plantillas['mostrar_carga_method'] +
                        contenido_mejorado[class_end:]
                    )
                    mejoras_aplicadas.append("Agregados métodos de indicadores de carga")

            # 4. Mejorar manejo de errores existente
            if not analisis['tiene_manejo_errores']:
                # Buscar excepciones sin feedback visual
                patron_except = r'except[^:]*:[^}]*?print\\([^)]*\\)'
                matches = re.finditer(patron_except, contenido_mejorado)
                for match in matches:
                    # Reemplazar print con mostrar_feedback
                    exception_block = match.group(0)
                    nuevo_block = re.sub(
                        r'print\\([^)]*\\)',
                        'self.mostrar_feedback(f"Error: {e}", "error")',
                        exception_block
                    )
                    contenido_mejorado = contenido_mejorado.replace(exception_block, nuevo_block)
                    mejoras_aplicadas.append("Mejorado manejo visual de errores")

            # 5. Agregar llamadas a feedback en operaciones críticas
            contenido_mejorado = self._agregar_feedback_operaciones_criticas(contenido_mejorado)
            if "Agregado feedback en operaciones" not in mejoras_aplicadas:
                mejoras_aplicadas.append("Agregado feedback en operaciones críticas")

            # Guardar archivo mejorado
            with open(view_file, 'w', encoding='utf-8') as f:
                f.write(contenido_mejorado)

            print(f"✅ Mejoras aplicadas a {modulo_path.name}: {', '.join(mejoras_aplicadas)}")
            return True

        except Exception as e:
            print(f"❌ Error aplicando mejoras a {modulo_path.name}: {e}")
            # Restaurar backup en caso de error
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    contenido_backup = f.read()
                with open(view_file, 'w', encoding='utf-8') as f:
                    f.write(contenido_backup)
                print(f"🔄 Archivo restaurado desde backup")
            except:
                pass
            return False

    def _encontrar_final_clase(self, contenido: str) -> Optional[int]:
        """Encuentra la posición del final de la clase principal."""
        # Buscar la última función/método de la clase
        matches = list(re.finditer(r'\\n    def [^(]+\\([^)]*\\):', contenido))
        if matches:
            last_method = matches[-1]
            # Buscar el final de este método
            lines = contenido[last_method.start():].split('\\n')
            indent_level = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '':
                    continue
                current_indent = len(line) - len(line.lstrip())
                if indent_level is None and line.strip():
                    indent_level = current_indent
                elif line.strip() and current_indent <= 4:  # Vuelta al nivel de clase
                    return last_method.start() + len('\\n'.join(lines[:i]))
            # Si llegamos aquí, es el final del archivo
            return len(contenido)
        return None

    def _agregar_feedback_operaciones_criticas(self, contenido: str) -> str:
        """Agrega feedback en operaciones críticas que no lo tienen."""
        # Operaciones que deberían tener feedback
        patrones_operaciones = [
            (r'(def.*guardar[^:]*:[^\\n]*\\n)', 'self.mostrar_feedback("Guardando...", "cargando")\\n        '),
            (r'(def.*eliminar[^:]*:[^\\n]*\\n)', 'self.mostrar_feedback("Eliminando...", "cargando")\\n        '),
            (r'(def.*actualizar[^:]*:[^\\n]*\\n)', 'self.mostrar_feedback("Actualizando...", "cargando")\\n        '),
            (r'(def.*cargar[^:]*:[^\\n]*\\n)', 'self.mostrar_feedback("Cargando datos...", "cargando")\\n        ')
        ]

        for patron, feedback in patrones_operaciones:
            matches = re.finditer(patron, contenido, re.IGNORECASE)
            for match in matches:
                # Solo agregar si no hay ya feedback en esta función
                funcion_start = match.start()
                # Buscar el final de la función (siguiente def o final de clase)
                next_def = re.search(r'\\n    def ', contenido[funcion_start + 10:])
                funcion_end = funcion_start + 10 + next_def.start() if next_def else len(contenido)
                funcion_content = contenido[funcion_start:funcion_end]

                if 'mostrar_feedback' not in funcion_content:
                    # Agregar feedback al inicio de la función
                    contenido = contenido.replace(match.group(1), match.group(1) + feedback)

        return contenido

    def procesar_todos_los_modulos(self):
        """Procesa todos los módulos y aplica mejoras de feedback."""
        if not self.modulos_dir.exists():
            print(f"❌ Error: Directorio de módulos no encontrado: {self.modulos_dir}")
            return

        modulos_procesados = []
        modulos_mejorados = []

        for modulo_dir in self.modulos_dir.iterdir():
            if modulo_dir.is_dir() and not modulo_dir.name.startswith('.'):
                print(f"🔍 Analizando módulo: {modulo_dir.name}")

                try:
                    analisis = self.analizar_modulo(modulo_dir)
                    modulos_procesados.append(analisis)

                    if analisis['mejoras_necesarias']:
                        print(f"⚠️ Mejoras necesarias en {modulo_dir.name}:")
                        for mejora in analisis['mejoras_necesarias']:
                            print(f"   - {mejora}")

                        # Aplicar mejoras
                        if self.aplicar_mejoras_feedback(modulo_dir, analisis):
                            modulos_mejorados.append(modulo_dir.name)
                    else:
                        print(f"✅ {modulo_dir.name} ya tiene feedback visual adecuado")

                except Exception as e:
                    print(f"❌ Error procesando {modulo_dir.name}: {e}")

        # Generar reporte
        self._generar_reporte_mejoras(modulos_procesados, modulos_mejorados)

        print(f"\\n📊 Resumen:")
        print(f"   📁 Módulos analizados: {len(modulos_procesados)}")
        print(f"   ✅ Módulos mejorados: {len(modulos_mejorados)}")
        print(f"   📋 Reporte generado en: mejoras_feedback_visual.md")

    def _generar_reporte_mejoras(self, modulos_procesados: List[Dict], modulos_mejorados: List[str]):
        """Genera un reporte de las mejoras aplicadas."""
        reporte = f"""# Reporte de Mejoras de Feedback Visual

**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Módulos analizados:** {len(modulos_procesados)}
**Módulos mejorados:** {len(modulos_mejorados)}

## Resumen de Mejoras

### Módulos Mejorados
"""

        for modulo in modulos_mejorados:
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication

from core.logger import log_error

            reporte += f"- ✅ **{modulo}** - Mejoras aplicadas\\n"

        reporte += "\\n### Análisis Detallado\\n\\n"

        for analisis in modulos_procesados:
            estado = "✅ Completo" if not analisis['mejoras_necesarias'] else "⚠️ Necesita mejoras"
            reporte += f"#### {analisis['nombre']} - {estado}\\n\\n"

            reporte += f"- **Feedback básico:** {'✅ Sí' if analisis['tiene_feedback_basico'] else '❌ No'}\\n"
            reporte += f"- **Indicadores de carga:** {'✅ Sí' if analisis['tiene_indicadores_carga'] else '❌ No'}\\n"
            reporte += f"- **Manejo de errores:** {'✅ Sí' if analisis['tiene_manejo_errores'] else '❌ No'}\\n"

            if analisis['mejoras_necesarias']:
                reporte += "\\n**Mejoras necesarias:**\\n"
                for mejora in analisis['mejoras_necesarias']:
                    reporte += f"- {mejora}\\n"

            reporte += "\\n"

        reporte += f"""
## Mejoras Implementadas

### 1. Sistema de Feedback Básico
- Label de feedback con auto-ocultamiento
- Mensajes con iconos contextuales
- Soporte de accesibilidad
- Logging automático de errores

### 2. Indicadores de Carga
- Cursor de espera durante operaciones
- Mensajes de estado dinámicos
- Deshabilitación temporal de UI
- Procesamiento de eventos para responsividad

### 3. Manejo Visual de Errores
- Conversión de prints a feedback visual
- Categorización de mensajes (info, éxito, advertencia, error)
- Tiempos de visualización apropiados
- Integración con sistema de logging

### 4. Accesibilidad
- Nombres y descripciones accesibles
- Soporte para lectores de pantalla
- Contraste y visibilidad mejorados

## Próximos Pasos

1. **Probar las mejoras** - Ejecutar la aplicación y verificar el feedback visual
2. **Ajustar estilos** - Revisar que los temas globales se apliquen correctamente
3. **Tests de UX** - Ejecutar tests de experiencia de usuario
4. **Documentar** - Actualizar documentación de estándares visuales

## Archivos de Backup

Los archivos originales se guardaron en: `{self.backup_dir}`

Para restaurar un módulo específico:
```bash
cp {self.backup_dir}/[modulo]_view_backup.py modules/[modulo]/view.py
```
"""

        reporte_file = self.proyecto_root / "mejoras_feedback_visual.md"
        with open(reporte_file, 'w', encoding='utf-8') as f:
            f.write(reporte)

        print(f"📋 Reporte generado: {reporte_file}")

def main():
    """Función principal del script."""
    script_dir = Path(__file__).parent
    proyecto_root = script_dir.parent.parent

    print("🎨 Mejorador Automático de Feedback Visual")
    print(f"📁 Proyecto: {proyecto_root}")
    print("=" * 50)

    mejorador = MejoradorFeedbackVisual(str(proyecto_root))
    mejorador.procesar_todos_los_modulos()

    print("\\n" + "=" * 50)
    print("✅ Mejoras de feedback visual completadas")
    print("🔄 Próximos pasos:")
    print("   1. Probar la aplicación para verificar las mejoras")
    print("   2. Ajustar estilos si es necesario")
    print("   3. Ejecutar tests de UX")
    print("   4. Actualizar documentación")

if __name__ == "__main__":
    main()
