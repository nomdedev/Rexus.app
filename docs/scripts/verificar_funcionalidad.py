#!/usr/bin/env python3
"""
Script para verificar que todos los módulos funcionen correctamente
con los datos poblados en la base de datos
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.database import InventarioDatabaseConnection, UsersDatabaseConnection, AuditoriaDatabaseConnection


class FunctionalityVerifier:
    """Clase para verificar funcionalidad del sistema"""
    
    def __init__(self):
        self.db_inventario = None
        self.db_users = None
        self.db_auditoria = None
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
    def connect_to_databases(self):
        """Conecta a las tres bases de datos"""
        try:
            self.db_inventario = InventarioDatabaseConnection()
            self.db_users = UsersDatabaseConnection()
            self.db_auditoria = AuditoriaDatabaseConnection()
            return True
        except Exception as e:
            self.errors.append(f"Error conectando a BD: {e}")
            return False
    
    def test_user_authentication(self):
        """Verifica que la autenticación funcione"""
        print("Verificando autenticación de usuarios...")
        self.total_tests += 1
        
        try:
            # Verificar usuarios existentes
            result = self.db_users.execute_query("SELECT COUNT(*) FROM usuarios WHERE estado = 'Activo'")
            if not result or result[0][0] == 0:
                self.errors.append("No hay usuarios activos en el sistema")
                return False
            
            user_count = result[0][0]
            print(f"  ✓ Encontrados {user_count} usuarios activos")
            
            # Verificar roles
            result = self.db_users.execute_query("SELECT DISTINCT rol FROM usuarios")
            roles = [row[0] for row in result] if result else []
            
            expected_roles = ['admin', 'supervisor', 'usuario']
            missing_roles = [role for role in expected_roles if role not in roles]
            
            if missing_roles:
                self.warnings.append(f"Roles faltantes: {missing_roles}")
            
            print(f"  ✓ Roles encontrados: {roles}")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando autenticación: {e}")
            return False
    
    def test_obras_module(self):
        """Verifica el módulo de obras"""
        print("Verificando módulo de obras...")
        self.total_tests += 1
        
        try:
            # Verificar obras existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM obras")
            if not result or result[0][0] == 0:
                self.errors.append("No hay obras en el sistema")
                return False
            
            obra_count = result[0][0]
            print(f"  ✓ Encontradas {obra_count} obras")
            
            # Verificar estados de obras
            result = self.db_inventario.execute_query("SELECT estado, COUNT(*) FROM obras GROUP BY estado")
            estados = {row[0]: row[1] for row in result} if result else {}
            
            print(f"  ✓ Estados de obras: {estados}")
            
            # Verificar obras con cliente
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM obras WHERE cliente IS NOT NULL AND cliente != ''")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} obras tienen cliente asignado")
            else:
                self.warnings.append("Algunas obras no tienen cliente asignado")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de obras: {e}")
            return False
    
    def test_herrajes_module(self):
        """Verifica el módulo de herrajes"""
        print("Verificando módulo de herrajes...")
        self.total_tests += 1
        
        try:
            # Verificar herrajes existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE activo = 1")
            if not result or result[0][0] == 0:
                self.errors.append("No hay herrajes activos en el sistema")
                return False
            
            herraje_count = result[0][0]
            print(f"  ✓ Encontrados {herraje_count} herrajes activos")
            
            # Verificar categorías
            result = self.db_inventario.execute_query("SELECT DISTINCT categoria FROM herrajes")
            categorias = [row[0] for row in result] if result else []
            print(f"  ✓ Categorías de herrajes: {categorias}")
            
            # Verificar stock
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE stock_actual > 0")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} herrajes tienen stock disponible")
            else:
                self.warnings.append("Ningún herraje tiene stock disponible")
            
            # Verificar stock bajo
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM herrajes WHERE stock_actual <= stock_minimo")
            if result and result[0][0] > 0:
                print(f"  ⚠ {result[0][0]} herrajes tienen stock bajo el mínimo")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de herrajes: {e}")
            return False
    
    def test_vidrios_module(self):
        """Verifica el módulo de vidrios"""
        print("Verificando módulo de vidrios...")
        self.total_tests += 1
        
        try:
            # Verificar vidrios existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM vidrios WHERE activo = 1")
            if not result or result[0][0] == 0:
                self.errors.append("No hay vidrios activos en el sistema")
                return False
            
            vidrio_count = result[0][0]
            print(f"  ✓ Encontrados {vidrio_count} vidrios activos")
            
            # Verificar tipos
            result = self.db_inventario.execute_query("SELECT DISTINCT tipo FROM vidrios")
            tipos = [row[0] for row in result] if result else []
            print(f"  ✓ Tipos de vidrios: {tipos}")
            
            # Verificar colores
            result = self.db_inventario.execute_query("SELECT DISTINCT color FROM vidrios")
            colores = [row[0] for row in result] if result else []
            print(f"  ✓ Colores disponibles: {colores}")
            
            # Verificar precios
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM vidrios WHERE precio_m2 > 0")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} vidrios tienen precio asignado")
            else:
                self.warnings.append("Algunos vidrios no tienen precio asignado")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de vidrios: {e}")
            return False
    
    def test_empleados_module(self):
        """Verifica el módulo de empleados"""
        print("Verificando módulo de empleados...")
        self.total_tests += 1
        
        try:
            # Verificar empleados existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados WHERE activo = 1")
            if not result or result[0][0] == 0:
                self.errors.append("No hay empleados activos en el sistema")
                return False
            
            empleado_count = result[0][0]
            print(f"  ✓ Encontrados {empleado_count} empleados activos")
            
            # Verificar cargos
            result = self.db_inventario.execute_query("SELECT DISTINCT cargo FROM empleados")
            cargos = [row[0] for row in result] if result else []
            print(f"  ✓ Cargos disponibles: {cargos}")
            
            # Verificar información completa
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados WHERE dni IS NOT NULL AND telefono IS NOT NULL")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} empleados tienen información completa")
            else:
                self.warnings.append("Algunos empleados no tienen información completa")
            
            # Verificar salarios
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM empleados WHERE salario_base > 0")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} empleados tienen salario asignado")
            else:
                self.warnings.append("Algunos empleados no tienen salario asignado")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de empleados: {e}")
            return False
    
    def test_equipos_module(self):
        """Verifica el módulo de equipos"""
        print("Verificando módulo de equipos...")
        self.total_tests += 1
        
        try:
            # Verificar equipos existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM equipos WHERE activo = 1")
            if not result or result[0][0] == 0:
                self.errors.append("No hay equipos activos en el sistema")
                return False
            
            equipo_count = result[0][0]
            print(f"  ✓ Encontrados {equipo_count} equipos activos")
            
            # Verificar estados
            result = self.db_inventario.execute_query("SELECT estado, COUNT(*) FROM equipos GROUP BY estado")
            estados = {row[0]: row[1] for row in result} if result else {}
            print(f"  ✓ Estados de equipos: {estados}")
            
            # Verificar mantenimientos
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM equipos WHERE proxima_revision IS NOT NULL")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} equipos tienen mantenimiento programado")
            else:
                self.warnings.append("Algunos equipos no tienen mantenimiento programado")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de equipos: {e}")
            return False
    
    def test_proveedores_module(self):
        """Verifica el módulo de proveedores"""
        print("Verificando módulo de proveedores...")
        self.total_tests += 1
        
        try:
            # Verificar proveedores existentes
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores")
            if not result or result[0][0] == 0:
                self.errors.append("No hay proveedores en el sistema")
                return False
            
            proveedor_count = result[0][0]
            print(f"  ✓ Encontrados {proveedor_count} proveedores")
            
            # Verificar información de contacto
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores WHERE telefono IS NOT NULL")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} proveedores tienen teléfono")
            else:
                self.warnings.append("Algunos proveedores no tienen teléfono")
            
            # Verificar email
            result = self.db_inventario.execute_query("SELECT COUNT(*) FROM proveedores WHERE email IS NOT NULL")
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} proveedores tienen email")
            else:
                self.warnings.append("Algunos proveedores no tienen email")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando módulo de proveedores: {e}")
            return False
    
    def test_database_relationships(self):
        """Verifica las relaciones entre tablas"""
        print("Verificando relaciones entre tablas...")
        self.total_tests += 1
        
        try:
            # Verificar relación obras-usuarios
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM obras o 
                WHERE EXISTS (
                    SELECT 1 FROM users.dbo.usuarios u 
                    WHERE u.usuario = o.usuario_creador
                )
            """)
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} obras tienen usuario creador válido")
            else:
                self.warnings.append("Algunas obras no tienen usuario creador válido")
            
            # Verificar relación herrajes-proveedores
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM herrajes h
                WHERE EXISTS (
                    SELECT 1 FROM proveedores p
                    WHERE p.nombre = h.proveedor
                )
            """)
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} herrajes tienen proveedor válido")
            else:
                self.warnings.append("Algunos herrajes no tienen proveedor válido")
            
            # Verificar relación vidrios-proveedores
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM vidrios v
                WHERE EXISTS (
                    SELECT 1 FROM proveedores p
                    WHERE p.nombre = v.proveedor
                )
            """)
            if result and result[0][0] > 0:
                print(f"  ✓ {result[0][0]} vidrios tienen proveedor válido")
            else:
                self.warnings.append("Algunos vidrios no tienen proveedor válido")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando relaciones: {e}")
            return False
    
    def test_data_consistency(self):
        """Verifica consistencia de datos"""
        print("Verificando consistencia de datos...")
        self.total_tests += 1
        
        try:
            # Verificar códigos únicos en herrajes
            result = self.db_inventario.execute_query("""
                SELECT codigo, COUNT(*) as count 
                FROM herrajes 
                GROUP BY codigo 
                HAVING COUNT(*) > 1
            """)
            if result and len(result) > 0:
                self.warnings.append(f"Códigos duplicados en herrajes: {[row[0] for row in result]}")
            else:
                print("  ✓ Códigos únicos en herrajes")
            
            # Verificar códigos únicos en empleados
            result = self.db_inventario.execute_query("""
                SELECT codigo, COUNT(*) as count 
                FROM empleados 
                GROUP BY codigo 
                HAVING COUNT(*) > 1
            """)
            if result and len(result) > 0:
                self.warnings.append(f"Códigos duplicados en empleados: {[row[0] for row in result]}")
            else:
                print("  ✓ Códigos únicos en empleados")
            
            # Verificar códigos únicos en equipos
            result = self.db_inventario.execute_query("""
                SELECT codigo, COUNT(*) as count 
                FROM equipos 
                GROUP BY codigo 
                HAVING COUNT(*) > 1
            """)
            if result and len(result) > 0:
                self.warnings.append(f"Códigos duplicados en equipos: {[row[0] for row in result]}")
            else:
                print("  ✓ Códigos únicos en equipos")
            
            # Verificar DNIs únicos
            result = self.db_inventario.execute_query("""
                SELECT dni, COUNT(*) as count 
                FROM empleados 
                WHERE dni IS NOT NULL
                GROUP BY dni 
                HAVING COUNT(*) > 1
            """)
            if result and len(result) > 0:
                self.warnings.append(f"DNIs duplicados en empleados: {[row[0] for row in result]}")
            else:
                print("  ✓ DNIs únicos en empleados")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando consistencia: {e}")
            return False
    
    def test_performance_queries(self):
        """Verifica que las consultas importantes funcionen"""
        print("Verificando consultas de rendimiento...")
        self.total_tests += 1
        
        try:
            # Consulta de obras activas
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM obras 
                WHERE estado IN ('En Proceso', 'Activa')
            """)
            if result:
                print(f"  ✓ Consulta de obras activas: {result[0][0]} obras")
            
            # Consulta de stock bajo
            result = self.db_inventario.execute_query("""
                SELECT COUNT(*) FROM herrajes 
                WHERE stock_actual <= stock_minimo AND activo = 1
            """)
            if result:
                print(f"  ✓ Consulta de stock bajo: {result[0][0]} herrajes")
            
            # Consulta de empleados por cargo
            result = self.db_inventario.execute_query("""
                SELECT cargo, COUNT(*) as cantidad
                FROM empleados 
                WHERE activo = 1
                GROUP BY cargo
                ORDER BY cantidad DESC
            """)
            if result:
                print(f"  ✓ Consulta de empleados por cargo: {len(result)} categorías")
            
            # Consulta de equipos por estado
            result = self.db_inventario.execute_query("""
                SELECT estado, COUNT(*) as cantidad
                FROM equipos 
                WHERE activo = 1
                GROUP BY estado
            """)
            if result:
                print(f"  ✓ Consulta de equipos por estado: {len(result)} estados")
            
            self.success_count += 1
            return True
            
        except Exception as e:
            self.errors.append(f"Error verificando consultas: {e}")
            return False
    
    def generate_report(self):
        """Genera reporte de verificación"""
        print("\n" + "="*70)
        print("REPORTE DE VERIFICACIÓN DE FUNCIONALIDAD")
        print("="*70)
        
        print(f"\nRESUMEN:")
        print(f"  Total de pruebas: {self.total_tests}")
        print(f"  Pruebas exitosas: {self.success_count}")
        print(f"  Pruebas fallidas: {self.total_tests - self.success_count}")
        print(f"  Errores: {len(self.errors)}")
        print(f"  Advertencias: {len(self.warnings)}")
        
        if self.errors:
            print(f"\nERRORES:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\nADVERTENCIAS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"\nESTADO GENERAL:")
        if success_rate == 100 and not self.errors:
            print("  ✓ SISTEMA COMPLETAMENTE FUNCIONAL")
        elif success_rate >= 80:
            print("  ⚠ SISTEMA FUNCIONANDO CON ADVERTENCIAS")
        else:
            print("  ✗ SISTEMA CON PROBLEMAS CRÍTICOS")
        
        print(f"  Porcentaje de éxito: {success_rate:.1f}%")
        
        print(f"\nFECHA DE VERIFICACIÓN: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return success_rate >= 80
    
    def run_all_tests(self):
        """Ejecuta todas las verificaciones"""
        print("INICIANDO VERIFICACIÓN DE FUNCIONALIDAD DEL SISTEMA")
        print("="*60)
        
        if not self.connect_to_databases():
            print("ERROR: No se pudo conectar a las bases de datos")
            return False
        
        # Ejecutar todas las pruebas
        tests = [
            self.test_user_authentication,
            self.test_obras_module,
            self.test_herrajes_module,
            self.test_vidrios_module,
            self.test_empleados_module,
            self.test_equipos_module,
            self.test_proveedores_module,
            self.test_database_relationships,
            self.test_data_consistency,
            self.test_performance_queries
        ]
        
        for test in tests:
            try:
                test()
                print()
            except Exception as e:
                self.errors.append(f"Error ejecutando prueba {test.__name__}: {e}")
                print(f"  ✗ Error en prueba: {e}")
        
        return self.generate_report()
    
    def cleanup(self):
        """Limpia recursos"""
        if self.db_inventario:
            self.db_inventario.disconnect()
        if self.db_users:
            self.db_users.disconnect()
        if self.db_auditoria:
            self.db_auditoria.disconnect()


def main():
    """Función principal"""
    verifier = FunctionalityVerifier()
    
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