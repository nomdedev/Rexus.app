#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para generar informes de análisis de módulos y checklists específicos.
Ejecuta el analizador de estructura de módulos y notifica de los resultados.

Autor: Sistema
Fecha: Generado automáticamente
"""

# Obtener la ruta absoluta del directorio actual
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Añadir el directorio raíz al path para poder importar módulos del proyecto
sys.path.insert(0, root_dir)

def crear_directorios():
    """Crea los directorios necesarios si no existen."""
    directorios = [
        os.path.join(root_dir, "docs", "analisis_modulos"),
        os.path.join(root_dir, "docs", "checklists", "modulos")
    ]

    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
        print(f"Directorio creado/verificado: {directorio}")

def ejecutar_analisis():
    """Ejecuta el script de análisis de estructura de módulos."""
    analisis_script = os.path.join(script_dir, "analizar_estructura_modulos.py")

    if not os.path.exists(analisis_script):
        print(f"Error: No se encontró el script de análisis en {analisis_script}")
        return False

    print("Ejecutando análisis de estructura de módulos...")
    print("-" * 80)

    # Ejecutar el script
    try:
        # Cambiar al directorio raíz para asegurar rutas relativas correctas
        os.chdir(root_dir)

        # Usar exec para ejecutar el script en el mismo proceso
        with open(analisis_script, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # Ejecutar el script
        exec(script_content, {'__name__': '__main__'})

        print("-" * 80)
        print("Análisis completado exitosamente.")
        return True

    except Exception as e:
        print(f"Error al ejecutar el análisis: {e}")
        return False

def actualizar_indice_principal():
    """Actualiza el índice principal de checklists con referencias a los nuevos checklists específicos."""
    indice_path = os.path.join(root_dir, "docs", "checklists", "00_indice_checklists.md")

    # Si no existe el archivo, no hacer nada
    if not os.path.exists(indice_path):
        print(f"Advertencia: No se encontró el archivo de índice en {indice_path}")
        return

    # Leer el contenido actual
    with open(indice_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar si ya existe la sección de checklists de módulos
    seccion_existente = "## Checklists de Verificación por Módulo" in contenido

    # Preparar la nueva sección
    nueva_seccion = """
## Checklists de Verificación por Módulo

*Estos checklists fueron generados automáticamente basados en el análisis estructural de cada módulo.*

"""

    # Buscar los checklists generados
    checklists_modulos = []
    modulos_dir = os.path.join(root_dir, "modules")
    for modulo in os.listdir(modulos_dir):
        if os.path.isdir(os.path.join(modulos_dir, modulo)):
            checklist_path = os.path.join(root_dir, "docs", "checklists", f"verificacion_{modulo}.md")
            if os.path.exists(checklist_path):
                checklists_modulos.append((modulo, f"verificacion_{modulo}.md"))

    # Ordenar por nombre de módulo
    checklists_modulos.sort()

    # Añadir cada módulo a la sección
    for modulo, archivo in checklists_modulos:
        nueva_seccion += f"- [**Checklist del módulo {modulo}**]({archivo})  \n  *Verificación específica de UI, datos y tests para {modulo}*\n\n"

    # Actualizar el contenido
    if seccion_existente:
        # Reemplazar la sección existente
        patron = r"## Checklists de Verificación por Módulo.*?(?=\n## |$)"
        contenido_actualizado = re.sub(patron, nueva_seccion, contenido, flags=re.DOTALL)
    else:
        # Añadir después de la última sección existente
import os
import re
import sys
from datetime import datetime

        contenido_actualizado = contenido
        if "## " in contenido:
            ultima_seccion_pos = contenido.rindex("## ")
            ultima_seccion_fin = contenido.find("\n\n", ultima_seccion_pos)
            if ultima_seccion_fin == -1:
                contenido_actualizado += "\n\n" + nueva_seccion
            else:
                contenido_hasta_seccion = contenido[:ultima_seccion_fin+2]
                contenido_despues_seccion = contenido[ultima_seccion_fin+2:]
                contenido_actualizado = contenido_hasta_seccion + nueva_seccion + contenido_despues_seccion
        else:
            contenido_actualizado += "\n\n" + nueva_seccion

    # Guardar el contenido actualizado
    with open(indice_path, "w", encoding="utf-8") as f:
        f.write(contenido_actualizado)

    print(f"Índice de checklists actualizado: {indice_path}")

def actualizar_marco_metodologico():
    """Asegura que el marco metodológico existe y está actualizado."""
    marco_path = os.path.join(root_dir, "docs", "checklists", "01_marco_verificacion_modulos.md")

    # Si el archivo ya existe, no lo modificamos
    if os.path.exists(marco_path):
        print(f"El marco metodológico ya existe: {marco_path}")
        return

    # Contenido del marco metodológico
    contenido = """# Marco de Verificación de Módulos

Este documento establece el marco metodológico y los criterios para la verificación exhaustiva de cada módulo del sistema. Sirve como guía general para todos los checklists específicos por módulo.

## Objetivos de la Verificación

1. **Asegurar la calidad de la interfaz de usuario**
   - Verificar carga correcta de elementos visuales
   - Comprobar feedback visual adecuado
   - Validar experiencia de usuario coherente

2. **Garantizar la integridad de datos**
   - Verificar validación completa de entradas
   - Comprobar persistencia correcta en base de datos
   - Validar manejo adecuado de transacciones

3. **Validar la seguridad**
   - Verificar protección contra inyección SQL
   - Comprobar validación y sanitización de entradas
   - Validar gestión de permisos y accesos

4. **Evaluar la cobertura de tests**
   - Verificar cobertura de funcionalidades principales
   - Comprobar inclusión de edge cases
   - Validar tests de integración con otros módulos

## Metodología de Verificación

### 1. Análisis Preliminar

- Revisar la estructura del módulo para identificar:
  - Componentes de UI
  - Operaciones con base de datos
  - Validaciones existentes
  - Tests implementados

### 2. Verificación de UI

- **Carga de datos**
  - Verificar que todos los elementos visuales se cargan correctamente
  - Comprobar que los datos se muestran en los formatos adecuados
  - Validar comportamiento con diferentes tipos de datos (incluyendo extremos)

- **Feedback visual**
  - Verificar indicadores de progreso para operaciones largas
  - Comprobar mensajes de error, advertencia y éxito
  - Validar cambios de estado visual (habilitado/deshabilitado, seleccionado, etc.)

- **Experiencia de usuario**
  - Verificar navegación intuitiva y coherente
  - Comprobar accesibilidad (tamaños, contrastes, etc.)
  - Validar comportamiento responsive

### 3. Verificación de Operaciones de Datos

- **Validación de entradas**
  - Verificar validación de tipos de datos
  - Comprobar validación de formatos específicos (fechas, emails, etc.)
  - Validar manejo de valores nulos, vacíos o extremos

- **Operaciones con base de datos**
  - Verificar uso de utilidades de SQL seguro
  - Comprobar manejo adecuado de transacciones
  - Validar respuesta ante fallos de BD

- **Integridad relacional**
  - Verificar manejo correcto de relaciones entre entidades
  - Comprobar gestión de restricciones de integridad
  - Validar cascadas y propagación de cambios

### 4. Verificación de Seguridad

- **Prevención de inyección**
  - Verificar uso de consultas parametrizadas
  - Comprobar escapado de caracteres peligrosos
  - Validar uso de listas blancas para nombres de tablas y columnas

- **Validación de permisos**
  - Verificar comprobación de permisos antes de operaciones críticas
  - Comprobar registro de accesos y operaciones sensibles
  - Validar separación de roles y privilegios

### 5. Verificación de Tests

- **Cobertura funcional**
  - Verificar que cada funcionalidad crítica tiene tests
  - Comprobar pruebas de todas las ramas de lógica condicional
  - Validar escenarios típicos de uso

- **Edge cases**
  - Verificar tests con datos límite o extremos
  - Comprobar manejo de errores y excepciones
  - Validar comportamiento ante condiciones inusuales

- **Integración**
  - Verificar tests de interacción con otros módulos
  - Comprobar pruebas de flujos completos
  - Validar comportamiento en escenarios reales

## Criterios de Aceptación

Un módulo se considera verificado y aceptado cuando:

1. Todos los elementos de UI se cargan correctamente y ofrecen feedback adecuado
2. Todas las operaciones con datos incluyen validaciones y usan utilidades de SQL seguro
3. Los permisos se verifican correctamente en todas las operaciones sensibles
4. Existe cobertura de tests para al menos el 80% de las funcionalidades
5. Se han documentado y probado los edge cases relevantes
6. Todos los hallazgos críticos han sido corregidos

## Documentación de Hallazgos

Para cada hallazgo, documentar:

1. **Descripción** - Qué se encontró y dónde
2. **Impacto** - Gravedad y posibles consecuencias
3. **Recomendación** - Cómo debería corregirse
4. **Prioridad** - Alta/Media/Baja

## Plantilla de Registro

| ID | Componente | Hallazgo | Impacto | Recomendación | Prioridad | Estado |
|----|------------|----------|---------|---------------|-----------|--------|
| 01 |            |          |         |               |           |        |
| 02 |            |          |         |               |           |        |
| 03 |            |          |         |               |           |        |

---

## Historial de Revisiones

| Fecha | Versión | Descripción | Autor |
|-------|---------|-------------|-------|
| """ + datetime.now().strftime("%d/%m/%Y") + """ | 1.0.0 | Versión inicial | Sistema |
"""

    # Crear el archivo
    with open(marco_path, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Marco metodológico creado: {marco_path}")

def main():
    """Función principal."""
    print("=" * 80)
    print("GENERADOR DE INFORMES DE ANÁLISIS DE MÓDULOS Y CHECKLISTS")
    print("=" * 80)
    print()

    # Crear directorios necesarios
    crear_directorios()

    # Asegurar que el marco metodológico existe
    actualizar_marco_metodologico()

    # Ejecutar análisis
    exito = ejecutar_analisis()

    if exito:
        # Actualizar índice principal de checklists
        actualizar_indice_principal()

        print()
        print("=" * 80)
        print("PROCESO COMPLETADO CON ÉXITO")
        print("=" * 80)
        print()
        print(f"Se han generado informes detallados en:")
        print(f"- {os.path.join(root_dir, 'docs', 'analisis_modulos')}")
        print(f"- {os.path.join(root_dir, 'docs', 'checklists')}")
        print()
        print("Para comenzar la revisión, consulte:")
        print(f"1. El marco metodológico: docs/checklists/01_marco_verificacion_modulos.md")
        print(f"2. El resumen general: docs/analisis_modulos/resumen_analisis.md")
        print(f"3. Los checklists específicos por módulo: docs/checklists/verificacion_*.md")
    else:
        print()
        print("=" * 80)
        print("El proceso no pudo completarse correctamente.")
        print("Revise los errores y vuelva a intentarlo.")
        print("=" * 80)

if __name__ == "__main__":
    main()
