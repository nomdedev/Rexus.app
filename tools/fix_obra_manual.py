#!/usr/bin/env python3

def fix_obra_dialog():
    archivo = "rexus/modules/inventario/dialogs/seleccionar_obra_dialog.py"
    
    # Patrones de corrección específicos
    corrections = [
        # Corregir líneas después de try:
        ("        try:\n        # Simular carga", "        try:\n            # Simular carga"),
        ("        self.obras_disponibles = [", "            self.obras_disponibles = ["),
        ("        {\n        'id': 1,", "            {\n                'id': 1,"),
        ("        'codigo': 'OBR-001',", "                'codigo': 'OBR-001',"),
        ("        'nombre': 'Construcción Edificio Central',", "                'nombre': 'Construcción Edificio Central',"),
        ("        'descripcion': 'Construcción de edificio de oficinas de 5 pisos',", "                'descripcion': 'Construcción de edificio de oficinas de 5 pisos',"),
        ("        'estado': 'En Progreso',", "                'estado': 'En Progreso',"),
        ("        'fecha_inicio': '2024-01-15',", "                'fecha_inicio': '2024-01-15',"),
        ("        'presupuesto_total': 2500000.0,", "                'presupuesto_total': 2500000.0,"),
        ("        'cliente': 'Constructora ABC',", "                'cliente': 'Constructora ABC',"),
        ("        'ubicacion': 'Av. Principal 123'", "                'ubicacion': 'Av. Principal 123'"),
        ("        },", "            },"),
        ("        ]", "            ]"),
        ("        self.actualizar_tabla_obras()", "            self.actualizar_tabla_obras()"),
        ("        except Exception as e:", "        except Exception as e:"),
        ("        QMessageBox.warning(self, \"Advertencia\", f\"Error cargando obras: {str(e)}\")", "            QMessageBox.warning(self, \"Advertencia\", f\"Error cargando obras: {str(e)}\")"),
    ]
    
    with open(archivo, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar correcciones
    for old, new in corrections:
        content = content.replace(old, new)
    
    # Escribir archivo corregido
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("OK - Correcciones aplicadas")

if __name__ == "__main__":
    fix_obra_dialog()