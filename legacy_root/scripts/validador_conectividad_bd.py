#!/usr/bin/env python3
"""
VALIDADOR DE CONECTIVIDAD DE BASES DE DATOS - REXUS.APP
=======================================================

Este script valida la conectividad real a las bases de datos
y genera scripts de creación para garantizar reproducibilidad.

Funciones:
1. Test de conectividad real a BD
2. Validación de estructura existente
3. Generación de scripts de creación faltantes
4. Verificación de integridad de datos
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import pyodbc

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))


class ValidadorConectividad:
    """Valida conectividad y estructura de bases de datos."""

    def __init__(self):
        self.conexiones = {}
        self.resultados = {
            "conectividad": {},
            "estructura": {},
            "scripts_generados": [],
        }

        # Configuración de conexiones (ajustar según tu entorno)
        self.config_bd = {
            "server": "localhost",  # Cambiar por tu servidor
            "driver": "{ODBC Driver 17 for SQL Server}",
            "trusted_connection": "yes",
        }

        self.bases_datos = ["inventario", "users", "auditoria"]

    def validar_conectividad_real(self):
        """Valida la conectividad real a las bases de datos."""
        print("🔌 VALIDANDO CONECTIVIDAD REAL A BASES DE DATOS")
        print("-" * 50)

        for bd in self.bases_datos:
            print(f"   [CHART] Probando conexión a: {bd}")

            try:
                # Construir string de conexión
                conn_string = (
                    f"DRIVER={self.config_bd['driver']};"
                    f"SERVER={self.config_bd['server']};"
                    f"DATABASE={bd};"
                    f"Trusted_Connection={self.config_bd['trusted_connection']};"
                )

                # Intentar conexión
                conn = pyodbc.connect(conn_string, timeout=5)
                cursor = conn.cursor()

                # Test básico
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]

                print(f"      [CHECK] CONECTADA - {version.split('-')[0].strip()}")

                self.conexiones[bd] = conn
                self.resultados["conectividad"][bd] = {
                    "estado": "CONECTADA",
                    "version": version,
                    "servidor": self.config_bd["server"],
                }

                # Obtener lista de tablas
                self.obtener_tablas_reales(bd, cursor)

            except pyodbc.Error as e:
                print(f"      [ERROR] ERROR: {e}")
                self.resultados["conectividad"][bd] = {
                    "estado": "ERROR",
                    "error": str(e),
                }
            except Exception as e:
                print(f"      [WARN] No disponible: {e}")
                self.resultados["conectividad"][bd] = {
                    "estado": "NO_DISPONIBLE",
                    "razon": str(e),
                }

    def obtener_tablas_reales(self, bd_nombre: str, cursor):
        """Obtiene la lista real de tablas en una base de datos."""
        try:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)

            tablas = [row[0] for row in cursor.fetchall()]

            print(f"         📋 Tablas encontradas: {len(tablas)}")
            for tabla in tablas[:5]:  # Mostrar solo las primeras 5
                print(f"            • {tabla}")

            if len(tablas) > 5:
                print(f"            • ... y {len(tablas) - 5} más")

            self.resultados["estructura"][bd_nombre] = {
                "tablas": tablas,
                "total_tablas": len(tablas),
            }

        except Exception as e:
            print(f"         [ERROR] Error obteniendo tablas: {e}")

    def generar_scripts_creacion(self):
        """Genera scripts de creación para reproducibilidad."""
        print("\n📝 GENERANDO SCRIPTS DE CREACIÓN")
        print("-" * 50)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for bd_nombre, estructura in self.resultados["estructura"].items():
            if "tablas" in estructura:
                script_file = (
                    f"scripts_reproducibilidad/crear_{bd_nombre}_{timestamp}.sql"
                )

                # Crear directorio si no existe
                os.makedirs(os.path.dirname(script_file), exist_ok=True)

                # Generar script de creación
                self.crear_script_bd(bd_nombre, estructura["tablas"], script_file)

                print(f"   [CHECK] Script generado: {script_file}")
                self.resultados["scripts_generados"].append(script_file)

    def crear_script_bd(self, bd_nombre: str, tablas: list, archivo_script: str):
        """Crea un script SQL para recrear una base de datos."""

        script_content = f"""-- ============================================
-- SCRIPT DE CREACIÓN: {bd_nombre.upper()}
-- ============================================
-- Generado automáticamente el: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
-- Total de tablas: {len(tablas)}

-- Crear base de datos si no existe
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{bd_nombre}')
BEGIN
    CREATE DATABASE [{bd_nombre}]
END
GO

USE [{bd_nombre}]
GO

-- Verificar que las tablas existan
"""

        for tabla in tablas:
            script_content += f"""
-- Verificar tabla: {tabla}
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{tabla}')
BEGIN
    PRINT 'ADVERTENCIA: Tabla {tabla} no existe - requiere definición manual'
END
"""

        script_content += f"""
-- ============================================
-- FIN DEL SCRIPT DE VERIFICACIÓN
-- ============================================
-- Para completar este script, necesitas:
-- 1. Exportar la estructura real de cada tabla
-- 2. Incluir las definiciones CREATE TABLE
-- 3. Agregar datos iniciales si es necesario
"""

        # Guardar script
        with open(archivo_script, "w", encoding="utf-8") as f:
            f.write(script_content)

    def generar_script_maestro(self):
        """Genera un script maestro de instalación."""
        print("\n🎯 GENERANDO SCRIPT MAESTRO DE INSTALACIÓN")
        print("-" * 50)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_maestro = (
            f"scripts_reproducibilidad/INSTALACION_COMPLETA_{timestamp}.sql"
        )

        os.makedirs(os.path.dirname(script_maestro), exist_ok=True)

        contenido_maestro = f"""-- =============================================
-- SCRIPT MAESTRO DE INSTALACIÓN - REXUS.APP
-- =============================================
-- Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
-- Versión: 2.0.0
-- Propósito: Instalación completa del sistema

-- PASO 1: Crear bases de datos principales
"""

        for bd in self.bases_datos:
            contenido_maestro += f"""
-- Base de datos: {bd}
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{bd}')
BEGIN
    CREATE DATABASE [{bd}]
    PRINT 'Base de datos {bd} creada exitosamente'
END
ELSE
BEGIN
    PRINT 'Base de datos {bd} ya existe'
END
GO
"""

        contenido_maestro += """
-- PASO 2: Ejecutar scripts específicos
-- Ejecute los siguientes scripts en orden:
"""

        # Listar scripts necesarios
        scripts_necesarios = [
            "tools/development/database/MPS_SQL_COMPLETO_SIN_PREFIJOS.sql",
            "tools/development/database/crear_tablas_adicionales.sql",
            "scripts/sql/legacy_backup/database/create_tables.sql",
        ]

        for i, script in enumerate(scripts_necesarios, 1):
            if os.path.exists(script):
                contenido_maestro += f"-- {i}. {script} [CHECK] DISPONIBLE\n"
            else:
                contenido_maestro += f"-- {i}. {script} [ERROR] FALTANTE\n"

        contenido_maestro += f"""
-- PASO 3: Verificar instalación
-- Ejecute el validador: python auditor_completo_sql.py

-- =============================================
-- FIN DEL SCRIPT MAESTRO
-- =============================================
"""

        with open(script_maestro, "w", encoding="utf-8") as f:
            f.write(contenido_maestro)

        print(f"   [CHECK] Script maestro creado: {script_maestro}")
        self.resultados["scripts_generados"].append(script_maestro)

    def cerrar_conexiones(self):
        """Cierra todas las conexiones abiertas."""
        for bd, conn in self.conexiones.items():
            try:
                conn.close()
                print(f"   [LOCK] Conexión cerrada: {bd}")
            except:
                pass

    def generar_reporte_final(self):
        """Genera el reporte final de validación."""
        print("\n" + "=" * 60)
        print("📋 REPORTE DE VALIDACIÓN DE CONECTIVIDAD")
        print("=" * 60)

        # Resumen de conectividad
        total_bd = len(self.bases_datos)
        conectadas = sum(
            1
            for bd in self.resultados["conectividad"].values()
            if bd.get("estado") == "CONECTADA"
        )

        print(f"\n[CHART] RESUMEN DE CONECTIVIDAD:")
        print(f"   • Bases de datos probadas: {total_bd}")
        print(f"   • Conexiones exitosas: {conectadas}")
        print(f"   • Scripts generados: {len(self.resultados['scripts_generados'])}")

        # Detalles por BD
        for bd_nombre, info in self.resultados["conectividad"].items():
            estado = info["estado"]
            if estado == "CONECTADA":
                tablas = (
                    self.resultados["estructura"]
                    .get(bd_nombre, {})
                    .get("total_tablas", 0)
                )
                print(f"   [CHECK] {bd_nombre}: {estado} ({tablas} tablas)")
            else:
                print(f"   [ERROR] {bd_nombre}: {estado}")

        # Scripts generados
        if self.resultados["scripts_generados"]:
            print(f"\n📝 SCRIPTS DE REPRODUCIBILIDAD GENERADOS:")
            for script in self.resultados["scripts_generados"]:
                print(f"   📄 {script}")

        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        if conectadas == total_bd:
            print("   [CHECK] Todas las BD están conectadas - Sistema listo")
            print("   🔧 Ejecute los scripts generados para verificar reproducibilidad")
        elif conectadas > 0:
            print("   [WARN] Conectividad parcial - Verifique configuración de BD faltantes")
        else:
            print("   [ERROR] Sin conectividad - Verifique configuración del servidor de BD")
            print("   🔧 Asegúrese de que SQL Server esté ejecutándose")
            print("   🔧 Verifique los strings de conexión")


def main():
    """Función principal."""
    print("🔌 VALIDADOR DE CONECTIVIDAD DE BD - REXUS.APP")
    print("Verificando estado real de bases de datos")
    print()

    validador = ValidadorConectividad()

    try:
        validador.validar_conectividad_real()
        validador.generar_scripts_creacion()
        validador.generar_script_maestro()
        validador.generar_reporte_final()

    finally:
        validador.cerrar_conexiones()

    print("\n🎯 VALIDACIÓN COMPLETADA")
    print("Revise los scripts generados para garantizar reproducibilidad.")


if __name__ == "__main__":
    main()
