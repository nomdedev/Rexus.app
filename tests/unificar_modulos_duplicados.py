#!/usr/bin/env python3
"""
Script para unificar el módulo duplicado "Logistica" / "Logística" en la base de datos
Mantiene solo "Logística" (con tilde) y elimina "Logistica" (sin tilde)
"""

def unificar_modulo_logistica():
    """
    Unifica los módulos duplicados de Logística:
    - Mantiene "Logística" (con tilde)
    - Elimina "Logistica" (sin tilde)
    - Actualiza todas las referencias
    """

    db = DatabaseConnection()
    db.conectar_a_base('users')

    print("=== UNIFICACIÓN DE MÓDULO LOGÍSTICA ===")

    try:
        # 1. Verificar estado actual
        print("1. Verificando estado actual...")
        query_check = """
        SELECT modulo, COUNT(*) as count
        FROM permisos_modulos
        WHERE modulo LIKE '%ogística%' OR modulo LIKE '%ogistica%'
        GROUP BY modulo
        ORDER BY modulo
        """
        resultado_inicial = db.ejecutar_query(query_check)

        if resultado_inicial:
            print("   Estado inicial:")
            for row in resultado_inicial:
                print(f"   - '{row[0]}': {row[1]} registros")
        else:
            print("   ❌ No se encontraron registros de Logística")
            return False

        # 2. Actualizar registros de "Logistica" (sin tilde) a "Logística" (con tilde)
        print("\n2. Actualizando registros...")
        query_update = """
        UPDATE permisos_modulos
        SET modulo = 'Logística'
        WHERE modulo = 'Logistica'
        """

        # Ejecutar la actualización
        resultado_update = db.ejecutar_query(query_update)
        print("   ✅ Query de actualización ejecutada")

        # 3. Verificar resultado final
        print("\n3. Verificando resultado final...")
        resultado_final = db.ejecutar_query(query_check)

        if resultado_final:
            print("   Estado final:")
            total_logistica = 0
            for row in resultado_final:
                print(f"   - '{row[0]}': {row[1]} registros")
                if row[0] == 'Logística':
                    total_logistica = row[1]

            if len(resultado_final) == 1 and resultado_final[0][0] == 'Logística':
                print(f"\n✅ UNIFICACIÓN EXITOSA")
                print(f"   - Solo queda 'Logística' con {total_logistica} registros")
                print(f"   - Duplicado 'Logistica' eliminado")
                return True
            else:
                print(f"\n⚠️  Aún hay múltiples registros")
                return False
        else:
            print("   ❌ No se encontraron registros después de la actualización")
            return False

    except Exception as e:
        print(f"\n❌ Error durante la unificación: {e}")
        traceback.print_exc()
        return False
def verificar_otros_duplicados():
import traceback

from core.database import DatabaseConnection

    """Verifica si hay otros módulos duplicados en la base de datos"""

    db = DatabaseConnection()
    db.conectar_a_base('users')

    print("\n=== VERIFICACIÓN DE OTROS DUPLICADOS ===")

    try:
        # Buscar módulos que puedan tener duplicados por acentos o espacios
        query_duplicados = """
        SELECT
            modulo,
            COUNT(*) as count,
            LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(modulo, 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u')) as normalizado
        FROM permisos_modulos
        GROUP BY modulo
        HAVING COUNT(*) > 0
        ORDER BY normalizado, modulo
        """
        resultado = db.ejecutar_query(query_duplicados)

        if resultado:
            # Agrupar por nombre normalizado para detectar duplicados
            grupos = {}
            for row in resultado:
                modulo, count, normalizado = row[0], row[1], row[2]
                if normalizado not in grupos:
                    grupos[normalizado] = []
                grupos[normalizado].append((modulo, count))

            # Mostrar grupos con posibles duplicados
            duplicados_encontrados = False
            for normalizado, modulos in grupos.items():
                if len(modulos) > 1:
                    print(f"\n⚠️  Posibles duplicados para '{normalizado}':")
                    for modulo, count in modulos:
                        print(f"   - '{modulo}': {count} registros")
                    duplicados_encontrados = True

            if not duplicados_encontrados:
                print("✅ No se encontraron otros módulos duplicados")

            return not duplicados_encontrados
        else:
            print("❌ No se pudieron obtener los módulos")
            return False

    except Exception as e:
        print(f"❌ Error verificando duplicados: {e}")
        return False

def main():
    print("SCRIPT DE UNIFICACIÓN DE MÓDULOS DUPLICADOS")
    print("=" * 50)

    # Paso 1: Unificar Logística
    exito_logistica = unificar_modulo_logistica()

    # Paso 2: Verificar otros duplicados
    sin_otros_duplicados = verificar_otros_duplicados()

    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN DE LA UNIFICACIÓN")
    print("=" * 50)
    print(f"Logística unificada: {'✅' if exito_logistica else '❌'}")
    print(f"Sin otros duplicados: {'✅' if sin_otros_duplicados else '❌'}")

    if exito_logistica and sin_otros_duplicados:
        print("\n🎉 UNIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("   - Base de datos limpia de duplicados")
        print("   - El test automático debería pasar al 100% ahora")
    else:
        print("\n⚠️  REVISAR PROBLEMAS DETECTADOS")
        if not exito_logistica:
            print("   - Problema con unificación de Logística")
        if not sin_otros_duplicados:
            print("   - Hay otros módulos duplicados")

if __name__ == "__main__":
    main()
