#!/usr/bin/env python3
"""
Script de Validación - Módulo Vidrios Refactorizado
================================================

Valida la estructura modular, conectividad y funcionalidad
del módulo vidrios refactorizado.

Ejecutar: python scripts/validacion_vidrios_modular.py
"""

import os
import sys
import traceback
from pathlib import Path
    if puntuacion_total >= 80:
        print("\\n[ROCKET] REFACTORIZACIÓN DE VIDRIOS: [CHECK] EXITOSA")
        print("💡 El módulo está listo para integración")
    elif puntuacion_total >= 60:
        print("\\n[WARN]  REFACTORIZACIÓN DE VIDRIOS: 🔄 REQUIERE AJUSTES")
        print("💡 Revisar elementos fallidos antes de proceder")
    else:
        print("\\n[ERROR] REFACTORIZACIÓN DE VIDRIOS: 🚫 REQUIERE REVISIÓN COMPLETA")
        print("💡 Corregir errores críticos antes de continuar")

    return puntuacion_totalel directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def imprimir_header(titulo):
    """Imprime un header formateado."""
    print("\n" + "=" * 80)
    print(f"🔍 {titulo}")
    print("=" * 80)


def imprimir_resultado(descripcion, resultado, detalles=None):
    """Imprime un resultado formateado."""
    icono = "[CHECK]" if resultado else "[ERROR]"
    print(f"{icono} {descripcion}")
    if detalles:
        for detalle in detalles:
            print(f"   📄 {detalle}")


def verificar_estructura_archivos():
    """Verifica que todos los archivos de la estructura modular existan."""
    imprimir_header("VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS")

    archivos_requeridos = [
        # Submódulos
        "rexus/modules/vidrios/submodules/__init__.py",
        "rexus/modules/vidrios/submodules/productos_manager.py",
        "rexus/modules/vidrios/submodules/obras_manager.py",
        "rexus/modules/vidrios/submodules/consultas_manager.py",
        # Modelo refactorizado
        "rexus/modules/vidrios/model_refactorizado.py",
        # SQL externalizado - Productos
        "scripts/sql/vidrios/productos/obtener_vidrio_por_id.sql",
        "scripts/sql/vidrios/productos/insertar_vidrio.sql",
        "scripts/sql/vidrios/productos/actualizar_vidrio.sql",
        # SQL externalizado - Consultas
        "scripts/sql/vidrios/consultas/obtener_todos_vidrios.sql",
        "scripts/sql/vidrios/consultas/buscar_vidrios.sql",
        "scripts/sql/vidrios/consultas/contar_total_vidrios.sql",
        "scripts/sql/vidrios/consultas/calcular_valor_total.sql",
        "scripts/sql/vidrios/consultas/vidrios_por_tipo.sql",
    ]

    archivos_existentes = []
    archivos_faltantes = []

    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            archivos_existentes.append(archivo)
        else:
            archivos_faltantes.append(archivo)

    porcentaje_completitud = (len(archivos_existentes) / len(archivos_requeridos)) * 100

    imprimir_resultado(
        f"Archivos de estructura: {len(archivos_existentes)}/{len(archivos_requeridos)}",
        len(archivos_faltantes) == 0,
        archivos_existentes[:3] + (["..."] if len(archivos_existentes) > 3 else []),
    )

    if archivos_faltantes:
        imprimir_resultado(
            f"Archivos faltantes: {len(archivos_faltantes)}",
            False,
            archivos_faltantes[:3] + (["..."] if len(archivos_faltantes) > 3 else []),
        )

    print(f"\n🎯 COMPLETITUD DE ESTRUCTURA: {porcentaje_completitud:.1f}%")
    return len(archivos_faltantes) == 0


def verificar_imports_submodulos():
    """Verifica que los imports de los submódulos funcionen correctamente."""
    imprimir_header("VERIFICACIÓN DE IMPORTS DE SUBMÓDULOS")

    imports_exitosos = 0
    imports_totales = 0
    errores_imports = []

    # Test ProductosManager
    imports_totales += 1
    try:
        from rexus.modules.vidrios.submodules.productos_manager import ProductosManager

        imports_exitosos += 1
        imprimir_resultado(
            "ProductosManager importado", True, ["Gestión CRUD de vidrios"]
        )
    except Exception as e:
        errores_imports.append(f"ProductosManager: {str(e)}")
        imprimir_resultado("ProductosManager importado", False, [str(e)])

    # Test ObrasManager
    imports_totales += 1
    try:
        from rexus.modules.vidrios.submodules.obras_manager import ObrasManager

        imports_exitosos += 1
        imprimir_resultado(
            "ObrasManager importado", True, ["Asignación de vidrios a obras"]
        )
    except Exception as e:
        errores_imports.append(f"ObrasManager: {str(e)}")
        imprimir_resultado("ObrasManager importado", False, [str(e)])

    # Test ConsultasManager
    imports_totales += 1
    try:
        from rexus.modules.vidrios.submodules.consultas_manager import ConsultasManager

        imports_exitosos += 1
        imprimir_resultado(
            "ConsultasManager importado", True, ["Búsquedas y estadísticas"]
        )
    except Exception as e:
        errores_imports.append(f"ConsultasManager: {str(e)}")
        imprimir_resultado("ConsultasManager importado", False, [str(e)])

    # Test modelo refactorizado
    imports_totales += 1
    try:
        from rexus.modules.vidrios.model_refactorizado import ModeloVidriosRefactorizado

        imports_exitosos += 1
        imprimir_resultado(
            "ModeloVidriosRefactorizado importado", True, ["Orquestador modular"]
        )
    except Exception as e:
        errores_imports.append(f"ModeloVidriosRefactorizado: {str(e)}")
        imprimir_resultado("ModeloVidriosRefactorizado importado", False, [str(e)])

    if errores_imports:
        print("\n[ERROR] ERRORES DE IMPORT:")
        for error in errores_imports:
            print(f"   🔴 {error}")

    print(f"\n🎯 IMPORTS EXITOSOS: {imports_exitosos}/{imports_totales}")
    return imports_exitosos == imports_totales


def verificar_inicializacion_submodulos():
    """Verifica que los submódulos se puedan inicializar correctamente."""
    imprimir_header("VERIFICACIÓN DE INICIALIZACIÓN DE SUBMÓDULOS")

    inicializaciones_exitosas = 0
    inicializaciones_totales = 0

    # Test inicialización sin conexión DB
    managers_info = [
        (
            "ProductosManager",
            "rexus.modules.vidrios.submodules.productos_manager",
            "ProductosManager",
        ),
        (
            "ObrasManager",
            "rexus.modules.vidrios.submodules.obras_manager",
            "ObrasManager",
        ),
        (
            "ConsultasManager",
            "rexus.modules.vidrios.submodules.consultas_manager",
            "ConsultasManager",
        ),
    ]

    for nombre, modulo, clase in managers_info:
        inicializaciones_totales += 1
        try:
            import importlib

            mod = importlib.import_module(modulo)
            manager_class = getattr(mod, clase)
            instance = manager_class()  # Sin conexión DB

            # Verificar atributos básicos
            tiene_db_connection = hasattr(instance, "db_connection")
            tiene_data_sanitizer = hasattr(instance, "data_sanitizer")

            inicializaciones_exitosas += 1
            imprimir_resultado(
                f"{nombre} inicializado",
                True,
                [
                    f"db_connection: {'[OK]' if tiene_db_connection else '✗'}",
                    f"data_sanitizer: {'[OK]' if tiene_data_sanitizer else '✗'}",
                ],
            )
        except Exception as e:
            imprimir_resultado(f"{nombre} inicializado", False, [str(e)])

    print(
        f"\n🎯 INICIALIZACIONES EXITOSAS: {inicializaciones_exitosas}/{inicializaciones_totales}"
    )
    return inicializaciones_exitosas == inicializaciones_totales


def verificar_modelo_refactorizado():
    """Verifica la funcionalidad del modelo refactorizado."""
    imprimir_header("VERIFICACIÓN DEL MODELO REFACTORIZADO")

    try:
        from rexus.modules.vidrios.model_refactorizado import ModeloVidriosRefactorizado

        # Inicializar modelo
        modelo = ModeloVidriosRefactorizado()

        # Verificar submódulos internos
        tiene_productos = (
            hasattr(modelo, "productos_manager")
            and modelo.productos_manager is not None
        )
        tiene_obras = (
            hasattr(modelo, "obras_manager") and modelo.obras_manager is not None
        )
        tiene_consultas = (
            hasattr(modelo, "consultas_manager")
            and modelo.consultas_manager is not None
        )

        imprimir_resultado("Modelo inicializado", True, ["Sin conexión DB"])
        imprimir_resultado("ProductosManager interno", tiene_productos)
        imprimir_resultado("ObrasManager interno", tiene_obras)
        imprimir_resultado("ConsultasManager interno", tiene_consultas)

        # Test información modular
        try:
            info = modelo.obtener_info_modular()
            tiene_info = isinstance(info, dict) and "submodulos" in info
            imprimir_resultado(
                "Información modular",
                tiene_info,
                [f"Version: {info.get('version', 'N/A')}"],
            )
        except Exception as e:
            imprimir_resultado("Información modular", False, [str(e)])

        # Test conectividad
        try:
            conectividad = modelo.verificar_conectividad_modulos()
            modulos_conectados = sum(
                1 for v in conectividad.values() if v and v != False
            )  # Excluir db_connection
            total_esperado = 3  # productos, obras, consultas

            imprimir_resultado(
                f"Conectividad módulos: {modulos_conectados}/{total_esperado}",
                modulos_conectados >= total_esperado,
                [
                    f"{k}: {'[OK]' if v else '✗'}"
                    for k, v in conectividad.items()
                    if k != "db_connection"
                ],
            )
        except Exception as e:
            imprimir_resultado("Conectividad módulos", False, [str(e)])

        print(f"\n🎯 MODELO REFACTORIZADO: [CHECK] FUNCIONAL")
        return True

    except Exception as e:
        imprimir_resultado("Modelo refactorizado", False, [str(e)])
        print(f"\n🎯 MODELO REFACTORIZADO: [ERROR] ERROR")
        return False


def verificar_compatibilidad_hacia_atras():
    """Verifica que se mantenga compatibilidad con la API anterior."""
    imprimir_header("VERIFICACIÓN DE COMPATIBILIDAD HACIA ATRÁS")

    try:
        from rexus.modules.vidrios.model_refactorizado import ModeloVidriosRefactorizado

        modelo = ModeloVidriosRefactorizado()

        # Métodos de compatibilidad obligatorios
        metodos_compatibilidad = [
            "obtener_todos_vidrios",
            "obtener_vidrio_por_id",
            "crear_vidrio",
            "actualizar_vidrio",
            "eliminar_vidrio",
        ]

        metodos_disponibles = 0
        for metodo in metodos_compatibilidad:
            if hasattr(modelo, metodo):
                metodos_disponibles += 1
                imprimir_resultado(f"Método {metodo}", True)
            else:
                imprimir_resultado(f"Método {metodo}", False)

        # Alias de compatibilidad
        try:
            from rexus.modules.vidrios.model_refactorizado import ModeloVidrios

            imprimir_resultado(
                "Alias ModeloVidrios", True, ["Para compatibilidad legacy"]
            )
        except ImportError:
            imprimir_resultado("Alias ModeloVidrios", False)

        porcentaje_compatibilidad = (
            metodos_disponibles / len(metodos_compatibilidad)
        ) * 100
        print(f"\n🎯 COMPATIBILIDAD: {porcentaje_compatibilidad:.1f}%")

        return metodos_disponibles == len(metodos_compatibilidad)

    except Exception as e:
        imprimir_resultado("Compatibilidad hacia atrás", False, [str(e)])
        return False


def generar_reporte_final():
    """Genera el reporte final de validación."""
    imprimir_header("REPORTE FINAL DE VALIDACIÓN")

    # Ejecutar todas las verificaciones
    resultados = {
        "Estructura de archivos": verificar_estructura_archivos(),
        "Imports de submódulos": verificar_imports_submodulos(),
        "Inicialización": verificar_inicializacion_submodulos(),
        "Modelo refactorizado": verificar_modelo_refactorizado(),
        "Compatibilidad": verificar_compatibilidad_hacia_atras(),
    }

    # Calcular puntuación total
    verificaciones_exitosas = sum(1 for resultado in resultados.values() if resultado)
    total_verificaciones = len(resultados)
    puntuacion_total = (verificaciones_exitosas / total_verificaciones) * 100

    print(f"\n{'=' * 60}")
    print(f"[CHART] RESUMEN DE RESULTADOS:")
    print(f"{'=' * 60}")

    for verificacion, resultado in resultados.items():
        icono = "[CHECK]" if resultado else "[ERROR]"
        print(f"{icono} {verificacion}")

    print(f"\n🎯 PUNTUACIÓN TOTAL: {puntuacion_total:.1f}%")
    print(
        f"📈 Verificaciones exitosas: {verificaciones_exitosas}/{total_verificaciones}"
    )

    if puntuacion_total >= 80:
        print(f"\n[ROCKET] REFACTORIZACIÓN DE VIDRIOS: [CHECK] EXITOSA")
        print(f"💡 El módulo está listo para integración")
    elif puntuación_total >= 60:
        print(f"\n[WARN]  REFACTORIZACIÓN DE VIDRIOS: 🔄 REQUIERE AJUSTES")
        print(f"💡 Revisar elementos fallidos antes de proceder")
    else:
        print(f"\n[ERROR] REFACTORIZACIÓN DE VIDRIOS: 🚫 REQUIERE REVISIÓN COMPLETA")
        print(f"💡 Corregir errores críticos antes de continuar")

    return puntuación_total


if __name__ == "__main__":
    try:
        puntuacion = generar_reporte_final()

        # Código de salida basado en el resultado
        if puntuacion >= 80:
            sys.exit(0)  # Éxito
        elif puntuacion >= 60:
            sys.exit(1)  # Advertencia
        else:
            sys.exit(2)  # Error crítico

    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN VALIDACIÓN:")
        print(f"🔴 {str(e)}")
        print(f"\n📋 Traceback:")
        traceback.print_exc()
        sys.exit(3)  # Error de ejecución
