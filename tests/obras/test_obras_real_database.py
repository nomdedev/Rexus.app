"""
Test de integración para verificar datos reales de obras en SQL Server.
Verifica la estructura de datos, cantidad de obras y coherencia con el modelo.
"""

import sys
import os
from typing import List, Tuple, Dict, Any

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.model import ObrasModel


class TestObrasRealDatabase:
    """Test para verificar datos reales de obras en SQL Server."""
    
    def __init__(self):
        self.model = None
        self.connection = None
    
    def setup_database_connection(self):
        """Configurar conexión a la base de datos real."""
        try:
            # Importar la conexión de inventario (donde están las obras)
            from rexus.core.database import get_inventario_connection
            
            db_conn = get_inventario_connection(auto_connect=True)
            if db_conn.connection:
                self.connection = db_conn.connection
                self.model = ObrasModel(self.connection)
                print("[CHECK] [DB TEST] Conexión establecida correctamente")
                return True
            else:
                print("[ERROR] [DB TEST] No se pudo conectar a la base de datos")
                return False
        except Exception as e:
            print(f"[ERROR] [DB TEST] Error configurando conexión: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verificar_tabla_obras_existe(self):
        """Verificar que la tabla obras existe y tiene la estructura esperada."""
        try:
            cursor = self.connection.cursor()
            
            # Verificar si la tabla existe
            query_exists = """
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'obras'
            """
            cursor.execute(query_exists)
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                print("[ERROR] [DB TEST] La tabla 'obras' no existe")
                return False
            
            print("[CHECK] [DB TEST] La tabla 'obras' existe")
            
            # Obtener estructura de columnas
            query_columns = """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'obras'
            ORDER BY ORDINAL_POSITION
            """
            cursor.execute(query_columns)
            columns = cursor.fetchall()
            
            print(f"📋 [DB TEST] Estructura de la tabla obras ({len(columns)} columnas):")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"[ERROR] [DB TEST] Error verificando tabla: {e}")
            return False
    
    def contar_obras_totales(self):
        """Contar el total de obras en la base de datos."""
        try:
            cursor = self.connection.cursor()
            
            # Total de obras
            cursor.execute("SELECT COUNT(*) FROM obras")
            total_obras = cursor.fetchone()[0]
            
            # Obras activas
            cursor.execute("SELECT COUNT(*) FROM obras WHERE activo = 1")
            obras_activas = cursor.fetchone()[0]
            
            # Obras inactivas
            obras_inactivas = total_obras - obras_activas
            
            print(f"[CHART] [DB TEST] Estadísticas de obras:")
            print(f"   - Total de obras: {total_obras}")
            print(f"   - Obras activas: {obras_activas}")
            print(f"   - Obras inactivas: {obras_inactivas}")
            
            cursor.close()
            return total_obras, obras_activas
            
        except Exception as e:
            print(f"[ERROR] [DB TEST] Error contando obras: {e}")
            return 0, 0
    
    def verificar_metodos_modelo(self):
        """Verificar que los métodos del modelo funcionan correctamente."""
        print(f"\n🔧 [DB TEST] Verificando métodos del modelo...")
        
        try:
            # Test obtener_todas_obras
            obras = self.model.obtener_todas_obras()
            print(f"   - obtener_todas_obras(): {len(obras)} obras obtenidas")
            
            if obras:
                primera_obra = obras[0]
                print(f"   - Estructura de datos (primera obra): {len(primera_obra)} campos")
                print(f"   - Ejemplo: {primera_obra[:5]}..." if len(primera_obra) > 5 else f"   - Ejemplo: {primera_obra}")
            
            # Test obtener_datos_paginados
            obras_pag, total = self.model.obtener_datos_paginados(0, 5)
            print(f"   - obtener_datos_paginados(0, 5): {len(obras_pag)} obras, total: {total}")
            
            # Test validar_obra_duplicada
            if obras:
                primer_codigo = obras[0][1] if len(obras[0]) > 1 else "TEST"
                es_duplicado = self.model.validar_obra_duplicada(primer_codigo)
                print(f"   - validar_obra_duplicada('{primer_codigo}'): {es_duplicado}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] [DB TEST] Error verificando métodos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verificar_coherencia_datos(self):
        """Verificar coherencia entre datos y estructura esperada por la vista."""
        print(f"\n🔍 [DB TEST] Verificando coherencia de datos...")
        
        try:
            obras = self.model.obtener_todas_obras()
            
            if not obras:
                print("[WARN] [DB TEST] No hay obras para verificar")
                return True
            
            # Verificar estructura esperada por la vista
            campos_esperados = [
                "id", "codigo_obra", "nombre", "descripcion", "cliente_id",
                "fecha_inicio", "fecha_fin_estimada", "fecha_fin_real",
                "etapa_actual", "estado", "porcentaje_completado",
                "presupuesto_inicial", "costo_actual", "margen_estimado",
                "ubicacion", "responsable_obra", "observaciones",
                "activo", "fecha_creacion", "fecha_actualizacion"
            ]
            
            primera_obra = obras[0]
            print(f"   - Campos esperados: {len(campos_esperados)}")
            print(f"   - Campos obtenidos: {len(primera_obra)}")
            
            if len(primera_obra) >= len(campos_esperados):
                print("[CHECK] [DB TEST] La estructura tiene suficientes campos")
                
                # Mapear algunos campos clave para la vista
                mapeo_vista = {
                    'id': primera_obra[0] if len(primera_obra) > 0 else None,
                    'codigo': primera_obra[1] if len(primera_obra) > 1 else None,
                    'nombre': primera_obra[2] if len(primera_obra) > 2 else None,
                    'cliente': primera_obra[4] if len(primera_obra) > 4 else None,
                    'fecha_inicio': primera_obra[5] if len(primera_obra) > 5 else None,
                    'estado': primera_obra[9] if len(primera_obra) > 9 else None,
                    'presupuesto': primera_obra[11] if len(primera_obra) > 11 else None,
                    'responsable': primera_obra[15] if len(primera_obra) > 15 else None,
                }
                
                print("   - Mapeo de campos clave para la vista:")
                for campo, valor in mapeo_vista.items():
                    print(f"     {campo}: {valor}")
                
            else:
                print(f"[WARN] [DB TEST] Posible problema: se esperan {len(campos_esperados)} campos, se obtuvieron {len(primera_obra)}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] [DB TEST] Error verificando coherencia: {e}")
            return False
    
    def ejecutar_test_completo(self):
        """Ejecutar test completo de verificación."""
        print("[ROCKET] [DB TEST] Iniciando test de base de datos real para obras...")
        print("=" * 60)
        
        # 1. Configurar conexión
        if not self.setup_database_connection():
            print("[ERROR] [DB TEST] Test fallido: No se pudo conectar a la base de datos")
            return False
        
        # 2. Verificar tabla
        if not self.verificar_tabla_obras_existe():
            print("[ERROR] [DB TEST] Test fallido: Problema con la tabla obras")
            return False
        
        # 3. Contar obras
        total, activas = self.contar_obras_totales()
        if total == 0:
            print("[WARN] [DB TEST] Advertencia: No hay obras en la base de datos")
        
        # 4. Verificar métodos del modelo
        if not self.verificar_metodos_modelo():
            print("[ERROR] [DB TEST] Test fallido: Problemas con métodos del modelo")
            return False
        
        # 5. Verificar coherencia
        if not self.verificar_coherencia_datos():
            print("[ERROR] [DB TEST] Test fallido: Problemas de coherencia de datos")
            return False
        
        print("=" * 60)
        print("[CHECK] [DB TEST] Test completado exitosamente")
        print(f"[CHART] [DB TEST] Resumen: {total} obras totales, {activas} activas")
        
        return True


def main():
    """Función principal para ejecutar el test."""
    test = TestObrasRealDatabase()
    success = test.ejecutar_test_completo()
    
    if success:
        print("\n🎉 Todos los tests pasaron correctamente")
        return 0
    else:
        print("\n💥 Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
