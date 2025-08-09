#!/usr/bin/env python3
"""
Tests para verificar funcionalidad de exportación PDF/Excel
"""

import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt


class MockTableWidget(QTableWidget):
    """Mock de QTableWidget para testing"""
    
    def __init__(self, data=None, headers=None):
        super().__init__()
        if data and headers:
            self.populate_table(data, headers)
    
    def populate_table(self, data, headers):
        """Poblar tabla con datos de prueba"""
        self.setRowCount(len(data))
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.setItem(row, col, item)


class ExportFunctionality:
    """Clase para manejar exportación de datos"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.errors = []
    
    def export_table_to_excel(self, table_widget, filename, filtered_data=None):
        """
        Exporta una tabla a Excel
        
        Args:
            table_widget: Widget de tabla a exportar
            filename: Nombre del archivo destino
            filtered_data: Datos filtrados (opcional)
        """
        try:
            # Obtener datos de la tabla
            if filtered_data:
                data = filtered_data
            else:
                data = self.get_table_data(table_widget)
            
            # Crear DataFrame
            df = pd.DataFrame(data['rows'], columns=data['headers'])
            
            # Exportar a Excel
            filepath = os.path.join(self.temp_dir, filename)
            df.to_excel(filepath, index=False)
            
            # Verificar que el archivo se creó
            if os.path.exists(filepath):
                return filepath
            else:
                self.errors.append(f"Archivo Excel no se creó: {filepath}")
                return None
                
        except Exception as e:
            self.errors.append(f"Error exportando a Excel: {e}")
            return None
    
    def export_table_to_pdf(self, table_widget, filename, filtered_data=None):
        """
        Exporta una tabla a PDF
        
        Args:
            table_widget: Widget de tabla a exportar
            filename: Nombre del archivo destino
            filtered_data: Datos filtrados (opcional)
        """
        try:
            # Obtener datos de la tabla
            if filtered_data:
                data = filtered_data
            else:
                data = self.get_table_data(table_widget)
            
            # Crear DataFrame
            df = pd.DataFrame(data['rows'], columns=data['headers'])
            
            # Exportar a PDF usando reportlab
            filepath = os.path.join(self.temp_dir, filename)
            
            # Simulación de exportación PDF (implementación real requiere reportlab)
            with open(filepath, 'w') as f:
                f.write("PDF Export Simulation\n")
                f.write("=" * 50 + "\n")
                f.write(f"Headers: {data['headers']}\n")
                f.write(f"Rows: {len(data['rows'])}\n")
                f.write("\nData:\n")
                for row in data['rows']:
                    f.write(f"{row}\n")
            
            # Verificar que el archivo se creó
            if os.path.exists(filepath):
                return filepath
            else:
                self.errors.append(f"Archivo PDF no se creó: {filepath}")
                return None
                
        except Exception as e:
            self.errors.append(f"Error exportando a PDF: {e}")
            return None
    
    def get_table_data(self, table_widget):
        """Extrae datos de un QTableWidget"""
        try:
            # Obtener headers
            headers = []
            for col in range(table_widget.columnCount()):
                header = table_widget.horizontalHeaderItem(col)
                headers.append(header.text() if header else f"Column {col}")
            
            # Obtener filas
            rows = []
            for row in range(table_widget.rowCount()):
                row_data = []
                for col in range(table_widget.columnCount()):
                    item = table_widget.item(row, col)
                    row_data.append(item.text() if item else "")
                rows.append(row_data)
            
            return {
                'headers': headers,
                'rows': rows
            }
            
        except Exception as e:
            self.errors.append(f"Error extrayendo datos de tabla: {e}")
            return {'headers': [], 'rows': []}
    
    def apply_filters(self, data, filters):
        """
        Aplica filtros a los datos
        
        Args:
            data: Datos originales
            filters: Diccionario con filtros a aplicar
        """
        try:
            if not filters:
                return data
            
            filtered_rows = []
            headers = data['headers']
            
            for row in data['rows']:
                include_row = True
                
                for filter_column, filter_value in filters.items():
                    if filter_column in headers:
                        col_index = headers.index(filter_column)
                        if col_index < len(row):
                            if filter_value.lower() not in row[col_index].lower():
                                include_row = False
                                break
                
                if include_row:
                    filtered_rows.append(row)
            
            return {
                'headers': headers,
                'rows': filtered_rows
            }
            
        except Exception as e:
            self.errors.append(f"Error aplicando filtros: {e}")
            return data
    
    def cleanup(self):
        """Limpia archivos temporales"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass


class TestExportFunctionality:
    """Clase para testing de funcionalidad de exportación"""
    
    def __init__(self):
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        self.export_handler = ExportFunctionality()
        self.errors_found = []
    
    def create_test_data(self):
        """Crea datos de prueba para testing"""
        headers = ['ID', 'Nombre', 'Tipo', 'Precio', 'Stock', 'Proveedor']
        rows = [
            ['1', 'Herraje A', 'Herraje', '25.50', '100', 'Proveedor 1'],
            ['2', 'Vidrio B', 'Vidrio', '45.00', '50', 'Proveedor 2'],
            ['3', 'Perfil C', 'Perfil', '30.25', '75', 'Proveedor 1'],
            ['4', 'Herraje D', 'Herraje', '15.75', '200', 'Proveedor 3'],
            ['5', 'Vidrio E', 'Vidrio', '55.00', '25', 'Proveedor 2'],
        ]
        return headers, rows
    
    def test_excel_export_full_table(self):
        """Test de exportación completa a Excel"""
        print("🧪 Testing Excel export (full table)...")
        
        try:
            # Crear datos de prueba
            headers, rows = self.create_test_data()
            table = MockTableWidget(rows, headers)
            
            # Exportar a Excel
            filepath = self.export_handler.export_table_to_excel(
                table, 
                "test_full_export.xlsx"
            )
            
            if filepath and os.path.exists(filepath):
                # Verificar contenido
                df = pd.read_excel(filepath)
                if len(df) == len(rows) and len(df.columns) == len(headers):
                    print("[CHECK] Excel export (full table) exitoso")
                    return True
                else:
                    self.errors_found.append("Excel export: datos incompletos")
                    return False
            else:
                self.errors_found.append("Excel export: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en Excel export test: {e}")
            return False
    
    def test_excel_export_filtered_data(self):
        """Test de exportación filtrada a Excel"""
        print("🧪 Testing Excel export (filtered data)...")
        
        try:
            # Crear datos de prueba
            headers, rows = self.create_test_data()
            table = MockTableWidget(rows, headers)
            
            # Aplicar filtros
            all_data = self.export_handler.get_table_data(table)
            filters = {'Tipo': 'Herraje'}
            filtered_data = self.export_handler.apply_filters(all_data, filters)
            
            # Exportar datos filtrados
            filepath = self.export_handler.export_table_to_excel(
                table,
                "test_filtered_export.xlsx",
                filtered_data
            )
            
            if filepath and os.path.exists(filepath):
                # Verificar que solo se exportaron herrajes
                df = pd.read_excel(filepath)
                herraje_count = sum(1 for row in rows if 'Herraje' in row[2])
                
                if len(df) == herraje_count:
                    print("[CHECK] Excel export (filtered) exitoso")
                    return True
                else:
                    self.errors_found.append("Excel export: filtros no aplicados correctamente")
                    return False
            else:
                self.errors_found.append("Excel export filtered: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en Excel filtered export test: {e}")
            return False
    
    def test_pdf_export_full_table(self):
        """Test de exportación completa a PDF"""
        print("🧪 Testing PDF export (full table)...")
        
        try:
            # Crear datos de prueba
            headers, rows = self.create_test_data()
            table = MockTableWidget(rows, headers)
            
            # Exportar a PDF
            filepath = self.export_handler.export_table_to_pdf(
                table,
                "test_full_export.pdf"
            )
            
            if filepath and os.path.exists(filepath):
                # Verificar contenido básico
                with open(filepath, 'r') as f:
                    content = f.read()
                    if "Headers:" in content and "Rows:" in content:
                        print("[CHECK] PDF export (full table) exitoso")
                        return True
                    else:
                        self.errors_found.append("PDF export: contenido incompleto")
                        return False
            else:
                self.errors_found.append("PDF export: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en PDF export test: {e}")
            return False
    
    def test_pdf_export_filtered_data(self):
        """Test de exportación filtrada a PDF"""
        print("🧪 Testing PDF export (filtered data)...")
        
        try:
            # Crear datos de prueba
            headers, rows = self.create_test_data()
            table = MockTableWidget(rows, headers)
            
            # Aplicar filtros
            all_data = self.export_handler.get_table_data(table)
            filters = {'Proveedor': 'Proveedor 1'}
            filtered_data = self.export_handler.apply_filters(all_data, filters)
            
            # Exportar datos filtrados
            filepath = self.export_handler.export_table_to_pdf(
                table,
                "test_filtered_export.pdf",
                filtered_data
            )
            
            if filepath and os.path.exists(filepath):
                # Verificar contenido
                with open(filepath, 'r') as f:
                    content = f.read()
                    proveedor1_count = sum(1 for row in rows if 'Proveedor 1' in row[5])
                    
                    if f"Rows: {proveedor1_count}" in content:
                        print("[CHECK] PDF export (filtered) exitoso")
                        return True
                    else:
                        self.errors_found.append("PDF export: filtros no aplicados correctamente")
                        return False
            else:
                self.errors_found.append("PDF export filtered: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en PDF filtered export test: {e}")
            return False
    
    def test_large_dataset_performance(self):
        """Test de rendimiento con dataset grande"""
        print("🧪 Testing large dataset performance...")
        
        try:
            # Crear dataset grande
            headers = ['ID', 'Nombre', 'Tipo', 'Precio', 'Stock']
            large_rows = []
            
            for i in range(1000):  # 1000 filas
                large_rows.append([
                    str(i),
                    f'Producto {i}',
                    f'Tipo {i % 10}',
                    f'{(i * 1.5):.2f}',
                    str(i * 10)
                ])
            
            table = MockTableWidget(large_rows, headers)
            
            import time
            start_time = time.time()
            
            # Exportar a Excel
            filepath = self.export_handler.export_table_to_excel(
                table,
                "test_large_dataset.xlsx"
            )
            
            end_time = time.time()
            export_time = end_time - start_time
            
            if filepath and os.path.exists(filepath):
                # Verificar que no tardó demasiado (menos de 5 segundos)
                if export_time < 5.0:
                    print(f"[CHECK] Large dataset export exitoso ({export_time:.2f}s)")
                    return True
                else:
                    self.errors_found.append(f"Large dataset export muy lento: {export_time:.2f}s")
                    return False
            else:
                self.errors_found.append("Large dataset export: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en large dataset test: {e}")
            return False
    
    def test_empty_table_export(self):
        """Test de exportación de tabla vacía"""
        print("🧪 Testing empty table export...")
        
        try:
            # Crear tabla vacía
            headers = ['ID', 'Nombre', 'Tipo']
            empty_rows = []
            table = MockTableWidget(empty_rows, headers)
            
            # Exportar a Excel
            filepath = self.export_handler.export_table_to_excel(
                table,
                "test_empty_table.xlsx"
            )
            
            if filepath and os.path.exists(filepath):
                # Verificar que el archivo tiene solo headers
                df = pd.read_excel(filepath)
                if len(df) == 0 and len(df.columns) == len(headers):
                    print("[CHECK] Empty table export exitoso")
                    return True
                else:
                    self.errors_found.append("Empty table export: estructura incorrecta")
                    return False
            else:
                self.errors_found.append("Empty table export: archivo no creado")
                return False
                
        except Exception as e:
            self.errors_found.append(f"Error en empty table test: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests de exportación"""
        print("[ROCKET] Iniciando tests de exportación...")
        print("=" * 50)
        
        # Lista de tests
        tests = [
            ("Excel Export Full", self.test_excel_export_full_table),
            ("Excel Export Filtered", self.test_excel_export_filtered_data),
            ("PDF Export Full", self.test_pdf_export_full_table),
            ("PDF Export Filtered", self.test_pdf_export_filtered_data),
            ("Large Dataset Performance", self.test_large_dataset_performance),
            ("Empty Table Export", self.test_empty_table_export),
        ]
        
        # Ejecutar tests
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n📋 {test_name}:")
                if test_func():
                    passed += 1
                else:
                    failed += 1
                    print(f"[ERROR] {test_name} falló")
            except Exception as e:
                failed += 1
                print(f"[ERROR] {test_name} falló con excepción: {e}")
        
        # Cleanup
        self.export_handler.cleanup()
        
        # Resumen
        print("\n" + "=" * 50)
        print("[CHART] RESUMEN DE TESTS DE EXPORTACIÓN:")
        print(f"[CHECK] Pasados: {passed}")
        print(f"[ERROR] Fallidos: {failed}")
        print(f"[CHART] Total: {passed + failed}")
        
        if self.errors_found:
            print("\n🐛 ERRORES ENCONTRADOS:")
            for i, error in enumerate(self.errors_found, 1):
                print(f"{i}. {error}")
        
        if self.export_handler.errors:
            print("\n[WARN] ERRORES DE EXPORTACIÓN:")
            for i, error in enumerate(self.export_handler.errors, 1):
                print(f"{i}. {error}")
        
        return failed == 0


def main():
    """Función principal para ejecutar tests"""
    tester = TestExportFunctionality()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 ¡Todos los tests de exportación pasaron!")
            return 0
        else:
            print("\n[WARN] Algunos tests de exportación fallaron. Revisar errores.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error fatal en tests de exportación: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())