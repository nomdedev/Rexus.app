#!/usr/bin/env python3
"""
Tests simples de exportacion sin Unicode
"""

import sys
import os
import tempfile
import pandas as pd
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem


def test_export_functionality():
    """Test básico de exportación"""
    print("Iniciando tests de exportación...")
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Crear datos de prueba
    headers = ['ID', 'Nombre', 'Tipo', 'Precio', 'Stock']
    rows = [
        ['1', 'Producto A', 'Tipo 1', '25.50', '100'],
        ['2', 'Producto B', 'Tipo 2', '45.00', '50'],
        ['3', 'Producto C', 'Tipo 1', '30.25', '75'],
    ]
    
    errors = []
    
    try:
        # Test 1: Crear tabla con datos
        print("Test 1: Creando tabla con datos...")
        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        for row, row_data in enumerate(rows):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)
        
        print("OK - Tabla creada con datos")
        
        # Test 2: Exportar a Excel
        print("Test 2: Exportando a Excel...")
        
        # Extraer datos de la tabla
        table_data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            table_data.append(row_data)
        
        # Crear DataFrame
        df = pd.DataFrame(table_data, columns=headers)
        
        # Exportar a archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False)
            
            # Verificar que se creó el archivo
            if os.path.exists(tmp.name):
                # Verificar contenido
                df_read = pd.read_excel(tmp.name)
                if len(df_read) == len(rows):
                    print("OK - Exportación a Excel exitosa")
                else:
                    errors.append("Excel: datos incompletos")
            else:
                errors.append("Excel: archivo no creado")
        
        # Test 3: Filtrar datos
        print("Test 3: Probando filtros...")
        
        # Filtrar por tipo
        filtered_df = df[df['Tipo'] == 'Tipo 1']
        expected_count = sum(1 for row in rows if row[2] == 'Tipo 1')
        
        if len(filtered_df) == expected_count:
            print("OK - Filtros funcionan correctamente")
        else:
            errors.append("Filtros no funcionan")
        
        # Test 4: Exportar datos filtrados
        print("Test 4: Exportando datos filtrados...")
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            filtered_df.to_excel(tmp.name, index=False)
            
            if os.path.exists(tmp.name):
                df_filtered_read = pd.read_excel(tmp.name)
                if len(df_filtered_read) == expected_count:
                    print("OK - Exportación filtrada exitosa")
                else:
                    errors.append("Exportación filtrada: datos incorrectos")
            else:
                errors.append("Exportación filtrada: archivo no creado")
        
        # Test 5: Manejo de tabla vacía
        print("Test 5: Probando tabla vacía...")
        
        empty_df = pd.DataFrame(columns=headers)
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            empty_df.to_excel(tmp.name, index=False)
            
            if os.path.exists(tmp.name):
                df_empty_read = pd.read_excel(tmp.name)
                if len(df_empty_read) == 0 and len(df_empty_read.columns) == len(headers):
                    print("OK - Tabla vacía manejada correctamente")
                else:
                    errors.append("Tabla vacía: estructura incorrecta")
            else:
                errors.append("Tabla vacía: archivo no creado")
        
        # Resumen
        print("\n" + "=" * 40)
        print("RESUMEN DE TESTS DE EXPORTACIÓN:")
        print(f"Total de tests: 5")
        print(f"Errores encontrados: {len(errors)}")
        
        if errors:
            print("\nERRORES:")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}")
        else:
            print("Todos los tests de exportación pasaron!")
        
        return len(errors) == 0
        
    except Exception as e:
        print(f"Error fatal durante tests de exportación: {e}")
        return False


if __name__ == "__main__":
    success = test_export_functionality()
    sys.exit(0 if success else 1)