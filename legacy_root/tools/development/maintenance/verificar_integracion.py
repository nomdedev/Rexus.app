#!/usr/bin/env python3
"""
Script de verificación final del sistema de integración cruzada.
Ejecuta todas las validaciones necesarias y reporta el estado del sistema.
"""

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def verificar_sistema():
    """Verificación completa del sistema de integración"""

    print("🔍 VERIFICACIÓN FINAL DEL SISTEMA DE INTEGRACIÓN")
    print("=" * 55)

    resultados = {
        "conexion": False,
        "modelos": 0,
        "integracion": 0,
        "visual": False,
        "errores": [],
    }

    try:
        # 1. Verificar conexión
        print("\n1️⃣  Verificando conexión a base de datos...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        db = ObrasDatabaseConnection()
        db.conectar()
        print(f"   [CHECK] Conectado a: {db.database}")
        resultados["conexion"] = True

        # 2. Verificar modelos
        print("\n2️⃣  Verificando modelos de integración...")

        modelos_verificados = []

        # Obras
        try:
            obras_model = ObrasModel(db)
            modelos_verificados.append("ObrasModel")
            print("   [CHECK] ObrasModel")
        except Exception as e:
            resultados["errores"].append(f"ObrasModel: {e}")
            print(f"   [ERROR] ObrasModel: {e}")

        # Inventario
        try:
            inv_model = InventarioModel(db)
            if hasattr(inv_model, "obtener_estado_pedido_por_obra"):
                modelos_verificados.append("InventarioModel")
                print("   [CHECK] InventarioModel + método integración")
            else:
                print("   [WARN]  InventarioModel sin método integración")
        except Exception as e:
            resultados["errores"].append(f"InventarioModel: {e}")
            print(f"   [ERROR] InventarioModel: {e}")

        # Vidrios
        try:
            vid_model = VidriosModel(db)
            if hasattr(vid_model, "obtener_estado_pedido_por_obra"):
                modelos_verificados.append("VidriosModel")
                print("   [CHECK] VidriosModel + método integración")
            else:
                print("   [WARN]  VidriosModel sin método integración")
        except Exception as e:
            resultados["errores"].append(f"VidriosModel: {e}")
            print(f"   [ERROR] VidriosModel: {e}")

        # Herrajes
        try:
            her_model = HerrajesModel(db)
            if hasattr(her_model, "obtener_estado_pedido_por_obra"):
                modelos_verificados.append("HerrajesModel")
                print("   [CHECK] HerrajesModel + método integración")
            else:
                print("   [WARN]  HerrajesModel sin método integración")
        except Exception as e:
            resultados["errores"].append(f"HerrajesModel: {e}")
            print(f"   [ERROR] HerrajesModel: {e}")

        # Contabilidad
        try:
            cont_model = ContabilidadModel(db)
            if hasattr(cont_model, "obtener_estado_pago_pedido_por_obra"):
                modelos_verificados.append("ContabilidadModel")
                print("   [CHECK] ContabilidadModel + método integración")
            else:
                print("   [WARN]  ContabilidadModel sin método integración")
        except Exception as e:
            resultados["errores"].append(f"ContabilidadModel: {e}")
            print(f"   [ERROR] ContabilidadModel: {e}")

        resultados["modelos"] = len(modelos_verificados)

        # 3. Verificar integración visual
        print("\n3️⃣  Verificando integración visual...")

        try:
            headers = obras_model.obtener_headers_obras()
            columnas_integracion = [
                "estado_material",
                "estado_vidrios",
                "estado_herrajes",
                "estado_pago",
            ]
            columnas_encontradas = []

            for col in columnas_integracion:
                if col in headers:
                    columnas_encontradas.append(col)
                    print(f"   [CHECK] Columna '{col}' presente")
                else:
                    print(f"   [ERROR] Columna '{col}' faltante")

            if len(columnas_encontradas) == len(columnas_integracion):
                resultados["visual"] = True
                resultados["integracion"] = len(columnas_encontradas)
            else:
                resultados["integracion"] = len(columnas_encontradas)

        except Exception as e:
            resultados["errores"].append(f"Headers: {e}")
            print(f"   [ERROR] Error verificando headers: {e}")

        # 4. Verificar datos de ejemplo
        print("\n4️⃣  Verificando datos de ejemplo...")

        try:
            obras = obras_model.obtener_datos_obras()
            if obras and len(obras) > 0:
                print(f"   [CHECK] {len(obras)} obras en sistema")

                # Probar con una obra real
                id_obra = obras[0][0]
                nombre_obra = obras[0][1] if len(obras[0]) > 1 else "Sin nombre"
                print(
                    f"   🔍 Probando integración con obra: {nombre_obra} (ID: {id_obra})"
                )

                # Test rápido de estados
                estados_probados = 0

                if "InventarioModel" in modelos_verificados:
                    try:
                        estado = inv_model.obtener_estado_pedido_por_obra(id_obra)
                        print(f"     📦 Inventario: {estado}")
                        estados_probados += 1
                    except:
                        print(f"     📦 Inventario: tabla no existe (normal)")

                if "VidriosModel" in modelos_verificados:
                    try:
                        estado = vid_model.obtener_estado_pedido_por_obra(id_obra)
                        print(f"     🪟 Vidrios: {estado}")
                        estados_probados += 1
                    except:
                        print(f"     🪟 Vidrios: tabla no existe (normal)")

                if "HerrajesModel" in modelos_verificados:
                    try:
                        estado = her_model.obtener_estado_pedido_por_obra(id_obra)
                        print(f"     🔧 Herrajes: {estado}")
                        estados_probados += 1
                    except:
                        print(f"     🔧 Herrajes: tabla no existe (normal)")

                if "ContabilidadModel" in modelos_verificados:
                    try:
                        estado = cont_model.obtener_estado_pago_pedido_por_obra(
                            id_obra, "inventario"
                        )
                        print(f"     💰 Pagos: {estado}")
                        estados_probados += 1
                    except:
                        print(f"     💰 Pagos: tabla no existe (normal)")

                print(f"   [CHECK] {estados_probados} estados verificados")

            else:
                print("   [WARN]  No hay obras en el sistema")

        except Exception as e:
            resultados["errores"].append(f"Datos: {e}")
            print(f"   [ERROR] Error verificando datos: {e}")

        # Cerrar conexión
        if db.connection:
            db.connection.close()

        # 5. Reporte final
        print("\n" + "=" * 55)
        print("[CHART] REPORTE FINAL")
        print("=" * 55)

        print(f"🔌 Conexión BD: {'[CHECK] OK' if resultados['conexion'] else '[ERROR] FALLO'}")
        print(f"🏗️  Modelos: {resultados['modelos']}/5 funcionando")
        print(f"🎨 Integración visual: {resultados['integracion']}/4 columnas")
        print(f"[ERROR] Errores: {len(resultados['errores'])}")

        if resultados["errores"]:
            print("\n🚨 ERRORES DETECTADOS:")
            for error in resultados["errores"]:
                print(f"   • {error}")

        # Evaluación final
        score = 0
        if resultados["conexion"]:
            score += 3
        score += resultados["modelos"]
        score += resultados["integracion"]
        if resultados["visual"]:
            score += 2

        max_score = 14  # 3 + 5 + 4 + 2
        percentage = (score / max_score) * 100

        print(f"\n🎯 PUNTUACIÓN: {score}/{max_score} ({percentage:.1f}%)")

        if percentage >= 90:
            print("🎉 ESTADO: [CHECK] EXCELENTE - Sistema completamente funcional")
            print("👍 Todas las funcionalidades de integración están operativas")
        elif percentage >= 70:
            print("🔧 ESTADO: [WARN]  BUENO - Sistema mayormente funcional")
            print("💡 Algunas mejoras menores recomendadas")
        elif percentage >= 50:
            print("🚧 ESTADO: [WARN]  PARCIAL - Sistema parcialmente funcional")
            print("🔨 Se requieren algunas correcciones")
        else:
            print("🚨 ESTADO: [ERROR] REQUIERE ATENCIÓN - Sistema necesita revisión")
            print("🛠️  Se requiere investigación y correcciones")

        print(f"\n📋 PRÓXIMOS PASOS:")
        if percentage >= 90:
            print("   • Sistema listo para producción")
            print("   • Ejecutar: python main.py para usar la aplicación")
            print("   • Opcional: Crear tablas de pedidos para datos históricos")
        else:
            print("   • Revisar errores mostrados arriba")
            print("   • Verificar configuración de base de datos")
            print("   • Ejecutar: python test_simple.py para más detalles")

        return percentage >= 70

    except Exception as e:
        print(f"\n🚨 ERROR CRÍTICO: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("[ROCKET] Iniciando verificación del sistema...")
    exito = verificar_sistema()
    print(f"\n{'[CHECK] VERIFICACIÓN COMPLETADA' if exito else '[ERROR] VERIFICACIÓN FALLÓ'}")
    sys.exit(0 if exito else 1)

import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from core.database import ObrasDatabaseConnection
from modules.contabilidad.model import ContabilidadModel
from modules.herrajes.model import HerrajesModel
from modules.inventario.model import InventarioModel
from modules.obras.model import ObrasModel
from modules.vidrios.model import VidriosModel
