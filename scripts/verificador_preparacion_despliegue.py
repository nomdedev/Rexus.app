#!/usr/bin/env python3
"""
🔍 Script final de verificación y preparación para despliegue
Validación completa del sistema Rexus.app antes de despliegue en producción
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import pyodbc


class VerificadorDespliegue:
    def __init__(self):
        self.base_path = Path.cwd()
        self.errores = []
        self.verificaciones = []

    def log_verificacion(self, modulo, estado, detalle=""):
        """Registra una verificación"""
        estado_emoji = "[CHECK]" if estado else "[ERROR]"
        mensaje = f"{estado_emoji} {modulo}: {detalle}"
        print(mensaje)

        self.verificaciones.append(
            {
                "modulo": modulo,
                "estado": estado,
                "detalle": detalle,
                "timestamp": datetime.now().isoformat(),
            }
        )

        if not estado:
            self.errores.append(f"{modulo}: {detalle}")

    def verificar_estructura_proyecto(self):
        """Verifica la estructura básica del proyecto"""
        print("\n🏗️ VERIFICANDO ESTRUCTURA DEL PROYECTO...")

        directorios_criticos = [
            "rexus",
            "rexus/core",
            "rexus/modules",
            "rexus/utils",
            "scripts",
            "scripts/sql",
            "config",
            "static",
            "templates",
        ]

        for directorio in directorios_criticos:
            path = self.base_path / directorio
            existe = path.exists() and path.is_dir()
            self.log_verificacion(
                f"Directorio {directorio}",
                existe,
                "Existe" if existe else "NO ENCONTRADO",
            )

    def verificar_archivos_criticos(self):
        """Verifica archivos críticos del sistema"""
        print("\n📄 VERIFICANDO ARCHIVOS CRÍTICOS...")

        archivos_criticos = [
            "main.py",
            "requirements.txt",
            "rexus/__init__.py",
            "rexus/core/module_manager.py",
            "rexus/utils/diagnostic_widget.py",
            "config/rexus_config.json",
        ]

        for archivo in archivos_criticos:
            path = self.base_path / archivo
            existe = path.exists() and path.is_file()
            tamaño = path.stat().st_size if existe else 0

            self.log_verificacion(
                f"Archivo {archivo}",
                existe and tamaño > 0,
                f"Existe ({tamaño} bytes)" if existe else "NO ENCONTRADO",
            )

    def verificar_scripts_sql(self):
        """Verifica scripts SQL esenciales"""
        print("\n🗄️ VERIFICANDO SCRIPTS SQL...")

        sql_dir = self.base_path / "scripts" / "sql"
        if not sql_dir.exists():
            self.log_verificacion(
                "Scripts SQL", False, "Directorio scripts/sql no existe"
            )
            return

        scripts_esenciales = ["inventario", "usuarios", "obras", "pedidos"]

        total_scripts = 0
        for script_dir in scripts_esenciales:
            path = sql_dir / script_dir
            if path.exists():
                sql_files = list(path.glob("*.sql"))
                total_scripts += len(sql_files)
                self.log_verificacion(
                    f"Scripts {script_dir}",
                    len(sql_files) > 0,
                    f"{len(sql_files)} archivos SQL",
                )
            else:
                self.log_verificacion(
                    f"Scripts {script_dir}", False, "Directorio no existe"
                )

        # Verificar script maestro de instalación
        scripts_reproducibilidad = self.base_path / "scripts_reproducibilidad"
        if scripts_reproducibilidad.exists():
            maestros = list(scripts_reproducibilidad.glob("INSTALACION_COMPLETA_*.sql"))
            self.log_verificacion(
                "Script maestro instalación",
                len(maestros) > 0,
                f"{len(maestros)} scripts maestros encontrados",
            )

    def verificar_conectividad_bd(self):
        """Verifica conectividad a bases de datos"""
        print("\n🔌 VERIFICANDO CONECTIVIDAD BASE DE DATOS...")

        try:
            # Intentar conexión SQL Server
            connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=localhost;"
                "Trusted_Connection=yes;"
            )

            conexion = pyodbc.connect(connection_string, timeout=10)
            cursor = conexion.cursor()

            # Verificar bases de datos
            databases = ["inventario", "users", "auditoria"]
            for db in databases:
                try:
                    cursor.execute(f"USE [{db}]")
                    cursor.execute("SELECT COUNT(*) FROM sys.tables")
                    tabla_count = cursor.fetchone()[0]

                    self.log_verificacion(
                        f"BD {db}", tabla_count > 0, f"{tabla_count} tablas encontradas"
                    )
                except Exception as e:
                    self.log_verificacion(f"BD {db}", False, f"Error: {str(e)}")

            cursor.close()
            conexion.close()

        except Exception as e:
            self.log_verificacion("Conectividad SQL Server", False, f"Error: {str(e)}")

    def verificar_dependencias_python(self):
        """Verifica dependencias de Python"""
        print("\n🐍 VERIFICANDO DEPENDENCIAS PYTHON...")

        dependencias_criticas = [
            "PyQt6",
            "pyodbc",
            "pandas",
            "openpyxl",
            "reportlab",
            "python-dotenv",
        ]

        for dependencia in dependencias_criticas:
            try:
                # Mapeo especial para módulos con nombres diferentes
                modulo_import = dependencia
                if dependencia == "python-dotenv":
                    modulo_import = "dotenv"
                else:
                    modulo_import = dependencia.replace("-", "_")

                __import__(modulo_import)
                self.log_verificacion(f"Dependencia {dependencia}", True, "Instalada")
            except ImportError:
                self.log_verificacion(
                    f"Dependencia {dependencia}", False, "NO INSTALADA"
                )

    def verificar_configuracion(self):
        """Verifica archivos de configuración"""
        print("\n⚙️ VERIFICANDO CONFIGURACIÓN...")

        config_path = self.base_path / "config" / "rexus_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # Verificar secciones críticas
                secciones = ["database", "security", "modules", "paths"]
                for seccion in secciones:
                    existe = seccion in config
                    self.log_verificacion(
                        f"Config {seccion}",
                        existe,
                        "Configurada" if existe else "Faltante",
                    )

            except Exception as e:
                self.log_verificacion("Configuración JSON", False, f"Error: {str(e)}")
        else:
            self.log_verificacion("Archivo configuración", False, "No existe")

    def verificar_modulos_aplicacion(self):
        """Verifica módulos de la aplicación"""
        print("\n📦 VERIFICANDO MÓDULOS DE APLICACIÓN...")

        modulos_path = self.base_path / "rexus" / "modules"
        if not modulos_path.exists():
            self.log_verificacion("Directorio módulos", False, "No existe")
            return

        modulos_esperados = [
            "inventario",
            "usuarios",
            "obras",
            "pedidos",
            "herrajes",
            "vidrios",
            "administracion",
            "mantenimiento",
            "logistica",
            "configuracion",
            "auditoria",
        ]

        for modulo in modulos_esperados:
            modulo_path = modulos_path / modulo
            view_file = modulo_path / "view.py"

            if view_file.exists():
                try:
                    # Verificar sintaxis básica
                    with open(view_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    compile(content, str(view_file), "exec")
                    self.log_verificacion(f"Módulo {modulo}", True, "Sintaxis OK")

                except SyntaxError as e:
                    self.log_verificacion(
                        f"Módulo {modulo}", False, f"Error sintaxis: {e}"
                    )
                except Exception as e:
                    self.log_verificacion(f"Módulo {modulo}", False, f"Error: {e}")
            else:
                self.log_verificacion(f"Módulo {modulo}", False, "view.py no existe")

    def verificar_secrets_hardcodeados(self):
        """Verifica que no existan contraseñas, claves, tokens o secretos hardcodeados en el código fuente."""
        print("\n[LOCK] VERIFICANDO QUE NO HAYA SECRETS HARDCODEADOS...")
        patrones = [
            r"password\s*=\s*['\"]",
            r"contraseña\s*=\s*['\"]",
            r"passwd\s*=\s*['\"]",
            r"clave\s*=\s*['\"]",
            r"pwd\s*=\s*['\"]",
            r"secret\s*=\s*['\"]",
            r"secreto\s*=\s*['\"]",
            r"api_key\s*=\s*['\"]",
            r"token\s*=\s*['\"]",
            r"AUTH\s*=\s*['\"]",
            r"USER\s*=\s*['\"]",
            r"PASS\s*=\s*['\"]",
        ]
        base = self.base_path
        encontrados = []
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.endswith(".py"):
                    path = Path(root) / file
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            contenido = f.read()
                        for patron in patrones:
                            import re

                            for match in re.finditer(patron, contenido):
                                linea = contenido[: match.start()].count("\n") + 1
                                encontrados.append((str(path), linea, match.group()))
                    except Exception as e:
                        self.log_verificacion(
                            f"Archivo {path}", False, f"Error leyendo: {e}"
                        )
        if encontrados:
            for archivo, linea, texto in encontrados:
                self.log_verificacion(
                    f"Secretos hardcodeados en {archivo}",
                    False,
                    f"Línea {linea}: {texto}",
                )
        else:
            self.log_verificacion(
                "Secrets hardcodeados", True, "No se encontraron en el código fuente"
            )

    def generar_reporte_final(self):
        """Genera reporte final de verificación"""
        print("\n" + "=" * 80)
        print("🎯 REPORTE FINAL DE VERIFICACIÓN PARA DESPLIEGUE")
        print("=" * 80)

        total_verificaciones = len(self.verificaciones)
        exitosas = sum(1 for v in self.verificaciones if v["estado"])
        fallidas = total_verificaciones - exitosas

        porcentaje_exito = (
            (exitosas / total_verificaciones * 100) if total_verificaciones > 0 else 0
        )

        print(f"\n[CHART] ESTADÍSTICAS:")
        print(f"   Total verificaciones: {total_verificaciones}")
        print(f"   [CHECK] Exitosas: {exitosas}")
        print(f"   [ERROR] Fallidas: {fallidas}")
        print(f"   📈 Porcentaje éxito: {porcentaje_exito:.1f}%")

        if porcentaje_exito >= 90:
            estado_general = "🎉 SISTEMA LISTO PARA DESPLIEGUE"
        elif porcentaje_exito >= 75:
            estado_general = "[WARN] SISTEMA REQUIERE CORRECCIONES MENORES"
        else:
            estado_general = "[ERROR] SISTEMA REQUIERE CORRECCIONES MAYORES"

        print(f"\n🏆 ESTADO GENERAL: {estado_general}")

        if self.errores:
            print(f"\n[ERROR] ERRORES ENCONTRADOS ({len(self.errores)}):")
            for i, error in enumerate(self.errores, 1):
                print(f"   {i}. {error}")

        # Guardar reporte en archivo
        reporte_path = (
            self.base_path
            / f"VERIFICACION_DESPLIEGUE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "estadisticas": {
                        "total": total_verificaciones,
                        "exitosas": exitosas,
                        "fallidas": fallidas,
                        "porcentaje_exito": porcentaje_exito,
                    },
                    "estado_general": estado_general,
                    "verificaciones": self.verificaciones,
                    "errores": self.errores,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"\n💾 Reporte guardado en: {reporte_path}")

        return porcentaje_exito >= 90

    def ejecutar_verificacion_completa(self):
        """Ejecuta verificación completa del sistema"""
        print("[ROCKET] INICIANDO VERIFICACIÓN COMPLETA PARA DESPLIEGUE")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Directorio: {self.base_path}")

        # Ejecutar todas las verificaciones
        self.verificar_estructura_proyecto()
        self.verificar_archivos_criticos()
        self.verificar_scripts_sql()
        self.verificar_conectividad_bd()
        self.verificar_dependencias_python()
        self.verificar_configuracion()
        self.verificar_modulos_aplicacion()
        self.verificar_secrets_hardcodeados()

        # Generar reporte final
        listo_para_despliegue = self.generar_reporte_final()

        return listo_para_despliegue


def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE PREPARACIÓN PARA DESPLIEGUE - REXUS.APP")
    print("=" * 60)

    verificador = VerificadorDespliegue()

    try:
        listo = verificador.ejecutar_verificacion_completa()

        if listo:
            print("\n🎉 ¡SISTEMA LISTO PARA DESPLIEGUE EN PRODUCCIÓN!")
            sys.exit(0)
        else:
            print("\n[WARN] Sistema requiere correcciones antes del despliegue")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Error durante verificación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
