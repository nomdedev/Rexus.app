#!/usr/bin/env python3
"""
Script para verificar funcionalidad del sistema - Version simple sin Unicode
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.database import InventarioDatabaseConnection, UsersDatabaseConnection


class SimpleFunctionalityVerifier:
    """Clase para verificar funcionalidad del sistema"""

    def __init__(self):
        self.db_inventario = None
        self.db_users = None
        self.results = []

    def connect_to_databases(self):
        """Conecta a las bases de datos"""
        try:
            self.db_inventario = InventarioDatabaseConnection()
            self.db_users = UsersDatabaseConnection()
            self.results.append("OK - Conexion a bases de datos establecida")
            return True
        except Exception as e:
            self.results.append(f"ERROR - Error conectando a BD: {e}")
            return False

    def test_users(self):
        """Verifica usuarios"""
        try:
            result = self.db_users.execute_query("SELECT COUNT(*) FROM usuarios WHERE estado = 'Activo'")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Usuarios activos: {result[0][0]}")

                # Verificar roles
                result = self.db_users.execute_query("SELECT DISTINCT rol FROM usuarios")
                roles = [row[0] for row in result] if result else []
                self.results.append(f"OK - Roles encontrados: {', '.join(roles)}")
                return True
            else:
                self.results.append("ERROR - No hay usuarios activos")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando usuarios: {e}")
            return False

    def test_obras(self):
        """Verifica obras"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM obras")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Obras encontradas: {result[0][0]}")

                # Estados de obras
                result = self.db_inventario.execute_query("SELECT estado, COUNT(*) FROM obras GROUP BY estado")
                estados = {row[0]: row[1] for row in result} if result else {}
                self.results.append(f"OK - Estados de obras: {estados}")
                return True
            else:
                self.results.append("ERROR - No hay obras")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando obras: {e}")
            return False

    def test_herrajes(self):
        """Verifica herrajes"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE activo = 1")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Herrajes activos: {result[0][0]}")

                # Stock disponible
                result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE stock_actual > 0")
                if result:
                    self.results.append(f"OK - Herrajes con stock: {result[0][0]}")

                # Stock bajo
                result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE stock_actual <= stock_minimo")
                if result:
                    self.results.append(f"INFO - Herrajes con stock bajo: {result[0][0]}")

                return True
            else:
                self.results.append("ERROR - No hay herrajes activos")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando herrajes: {e}")
            return False

    def test_vidrios(self):
        """Verifica vidrios"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM vidrios WHERE activo = 1")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Vidrios activos: {result[0][0]}")

                # Tipos de vidrios
                result = self.db_inventario.execute_query("SELECT DISTINCT tipo FROM vidrios")
                tipos = [row[0] for row in result] if result else []
                self.results.append(f"OK - Tipos de vidrios: {', '.join(tipos)}")

                return True
            else:
                self.results.append("ERROR - No hay vidrios activos")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando vidrios: {e}")
            return False

    def test_empleados(self):
        """Verifica empleados"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados WHERE activo = 1")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Empleados activos: {result[0][0]}")

                # Cargos
                result = self.db_inventario.execute_query("SELECT DISTINCT cargo FROM empleados")
                cargos = [row[0] for row in result] if result else []
                self.results.append(f"OK - Cargos disponibles: {len(cargos)}")

                return True
            else:
                self.results.append("ERROR - No hay empleados activos")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando empleados: {e}")
            return False

    def test_equipos(self):
        """Verifica equipos"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM equipos WHERE activo = 1")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Equipos activos: {result[0][0]}")

                # Estados
                result = self.db_inventario.execute_query("SELECT estado, COUNT(*) FROM equipos GROUP BY estado")
                estados = {row[0]: row[1] for row in result} if result else {}
                self.results.append(f"OK - Estados de equipos: {estados}")

                return True
            else:
                self.results.append("ERROR - No hay equipos activos")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando equipos: {e}")
            return False

    def test_proveedores(self):
        """Verifica proveedores"""
        try:
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores")
            if result and result[0][0] > 0:
                self.results.append(f"OK - Proveedores encontrados: {result[0][0]}")

                # Con información completa
                result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores WHERE telefono IS NOT NULL AND email IS NOT NULL")
                if result:
                    self.results.append(f"OK - Proveedores con info completa: {result[0][0]}")

                return True
            else:
                self.results.append("ERROR - No hay proveedores")
                return False
        except Exception as e:
            self.results.append(f"ERROR - Error verificando proveedores: {e}")
            return False

    def test_data_consistency(self):
        """Verifica consistencia de datos"""
        try:
            # Códigos únicos en herrajes
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM (
                    SELECT codigo FROM herrajes GROUP BY codigo HAVING COUNT(*) > 1
                ) duplicados
            """)
            if result and result[0][0] == 0:
                self.results.append("OK - Codigos unicos en herrajes")
            else:
                self.results.append(f"WARNING - Codigos duplicados en herrajes: {result[0][0]}")

            # Códigos únicos en empleados
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM (
                    SELECT codigo FROM empleados GROUP BY codigo HAVING COUNT(*) > 1
                ) duplicados
            """)
            if result and result[0][0] == 0:
                self.results.append("OK - Codigos unicos en empleados")
            else:
                self.results.append(f"WARNING - Codigos duplicados en empleados: {result[0][0]}")

            # Códigos únicos en equipos
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM (
                    SELECT codigo FROM equipos GROUP BY codigo HAVING COUNT(*) > 1
                ) duplicados
            """)
            if result and result[0][0] == 0:
                self.results.append("OK - Codigos unicos en equipos")
            else:
                self.results.append(f"WARNING - Codigos duplicados en equipos: {result[0][0]}")

            return True
        except Exception as e:
            self.results.append(f"ERROR - Error verificando consistencia: {e}")
            return False

    def test_performance_queries(self):
        """Verifica consultas importantes"""
        try:
            # Obras activas
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM obras WHERE estado IN ('En Proceso', 'Activa')
            """)
            if result:
                self.results.append(f"OK - Obras activas: {result[0][0]}")

            # Consulta de empleados por cargo
            result = self.db_inventario.execute_query("""
                SELECT COUNT(DISTINCT cargo) FROM empleados WHERE activo = 1
            """)
            if result:
                self.results.append(f"OK - Cargos diferentes: {result[0][0]}")

            # Equipos operativos
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM equipos WHERE estado = 'Operativo' AND activo = 1
            """)
            if result:
                self.results.append(f"OK - Equipos operativos: {result[0][0]}")

            return True
        except Exception as e:
            self.results.append(f"ERROR - Error en consultas: {e}")
            return False

    def run_all_tests(self):
        """Ejecuta todas las verificaciones"""
        print("VERIFICACION DE FUNCIONALIDAD DEL SISTEMA")
        print("=" * 50)

        if not self.connect_to_databases():
            print("ERROR: No se pudo conectar a las bases de datos")
            return False

        # Ejecutar todas las pruebas
        tests = [
            ("Usuarios", self.test_users),
            ("Obras", self.test_obras),
            ("Herrajes", self.test_herrajes),
            ("Vidrios", self.test_vidrios),
            ("Empleados", self.test_empleados),
            ("Equipos", self.test_equipos),
            ("Proveedores", self.test_proveedores),
            ("Consistencia", self.test_data_consistency),
            ("Consultas", self.test_performance_queries)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\nVerificando {test_name}...")
            try:
                if test_func():
                    passed += 1
                    print(f"  -> PASADO")
                else:
                    print(f"  -> FALLIDO")
            except Exception as e:
                print(f"  -> ERROR: {e}")

        # Mostrar resultados
        print("\n" + "=" * 50)
        print("RESULTADOS DETALLADOS:")
        print("=" * 50)

        for result in self.results:
            print(f"  {result}")

        print("\n" + "=" * 50)
        print("RESUMEN FINAL:")
        print("=" * 50)
        print(f"Pruebas pasadas: {passed}/{total}")
        print(f"Porcentaje de exito: {(passed/total)*100:.1f}%")

        if passed == total:
            print("ESTADO: SISTEMA COMPLETAMENTE FUNCIONAL")
        elif passed >= total * 0.8:
            print("ESTADO: SISTEMA FUNCIONANDO CON ADVERTENCIAS")
        else:
            print("ESTADO: SISTEMA CON PROBLEMAS CRITICOS")

        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return passed >= total * 0.8

    def cleanup(self):
        """Limpia recursos"""
        if self.db_inventario:
            self.db_inventario.disconnect()
        if self.db_users:
            self.db_users.disconnect()


def main():
    """Función principal"""
    verifier = SimpleFunctionalityVerifier()

    try:
        success = verifier.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"ERROR FATAL: {e}")
        return 1
    finally:
        verifier.cleanup()


if __name__ == "__main__":
    sys.exit(main())
