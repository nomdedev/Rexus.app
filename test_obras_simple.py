#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple para verificar carga de datos de obras
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath('.'))

def test_model_direct():
    """Test directo del modelo sin UI"""
    print("🧪 [TEST] Iniciando test directo del modelo...")
    
    try:
        from rexus.modules.obras.model import ObrasModel
        from rexus.core.database import get_inventario_connection
        
        # Conectar a la base de datos
        print("[TEST] Conectando a la base de datos...")
        db_conn = get_inventario_connection(auto_connect=True)
        
        if not db_conn.connection:
            print("❌ [TEST] No se pudo conectar a la base de datos")
            return False
            
        print("✅ [TEST] Conexión a base de datos exitosa")
        
        # Crear modelo
        print("[TEST] Creando modelo de obras...")
        model = ObrasModel(db_conn.connection)
        
        # Obtener obras
        print("[TEST] Obteniendo obras...")
        obras = model.obtener_todas_obras()
        
        print(f"📊 [TEST] Obras obtenidas: {len(obras) if obras else 0}")
        
        if obras:
            print(f"📋 [TEST] Primera obra: {obras[0][:5]}...")  # Solo primeros 5 campos
            print(f"📏 [TEST] Campos por obra: {len(obras[0])}")
            
            # Verificar campos específicos
            primera_obra = obras[0]
            print(f"🏷️ [TEST] ID: {primera_obra[0]}")
            print(f"🏷️ [TEST] Nombre: {primera_obra[1]}")
            print(f"🏷️ [TEST] Cliente: {primera_obra[5] if len(primera_obra) > 5 else 'N/A'}")
            print(f"🏷️ [TEST] Estado: {primera_obra[6] if len(primera_obra) > 6 else 'N/A'}")
            print(f"🏷️ [TEST] Código: {primera_obra[20] if len(primera_obra) > 20 else 'N/A'}")
            print(f"🏷️ [TEST] Responsable: {primera_obra[21] if len(primera_obra) > 21 else 'N/A'}")
            
        return True
        
    except Exception as e:
        print(f"❌ [TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_model_direct()
    sys.exit(0 if success else 1)
