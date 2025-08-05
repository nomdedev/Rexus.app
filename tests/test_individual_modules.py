import sys
import os
sys.path.insert(0, os.getcwd())

# Mockear PyQt6 para evitar GUI
class MockQt:
    class AlignmentFlag:
        AlignCenter = 0x0084
    class ItemDataRole:
        UserRole = 0x0100
    class Orientation:
        Horizontal = 0x1

class MockQWidget:
    def __init__(self): pass

class MockQPushButton:
    def __init__(self, text=""): pass
    def clicked(self): return self
    def connect(self, func): pass

class MockQTableWidget:
    def __init__(self): pass
    def setColumnCount(self, count): pass
    def setHorizontalHeaderLabels(self, labels): pass
    def setRowCount(self, count): pass
    def setItem(self, row, col, item): pass
    def setCellWidget(self, row, col, widget): pass
    def item(self, row, col): return MockQTableWidgetItem()
    def currentRow(self): return 0
    def itemSelectionChanged(self): return self
    def setAlternatingRowColors(self, enabled): pass
    def setSelectionBehavior(self, behavior): pass
    def setStyleSheet(self, style): pass
    def horizontalHeader(self): return MockQHeaderView()

class MockQTableWidgetItem:
    def __init__(self, text=""): 
        self.text_value = text
    def text(self): return self.text_value
    def setTextAlignment(self, alignment): pass
    def setData(self, role, data): pass
    def data(self, role): return 1

class MockQHeaderView:
    def setSectionResizeMode(self, mode): pass

class MockQVBoxLayout:
    def __init__(self, parent=None): pass
    def addWidget(self, widget): pass
    def addLayout(self, layout): pass
    def setSpacing(self, spacing): pass
    def setContentsMargins(self, *args): pass

class MockQHBoxLayout:
    def __init__(self): pass
    def addWidget(self, widget, stretch=0): pass
    def addStretch(self): pass

class MockQLabel:
    def __init__(self, text=""): pass
    def setStyleSheet(self, style): pass
    def setText(self, text): pass

class MockQLineEdit:
    def __init__(self): pass
    def setPlaceholderText(self, text): pass
    def textChanged(self): return self
    def connect(self, func): pass
    def text(self): return ""
    def clear(self): pass

class MockQComboBox:
    def __init__(self): pass
    def addItem(self, text): pass
    def addItems(self, items): pass
    def currentText(self): return ""
    def currentTextChanged(self): return self
    def connect(self, func): pass
    def setCurrentText(self, text): pass
    def setCurrentIndex(self, index): pass

class MockQGroupBox:
    def __init__(self, title=""): pass

# Mock PyQt6
sys.modules['PyQt6'] = type('MockModule', (), {})()
sys.modules['PyQt6.QtWidgets'] = type('MockModule', (), {
    'QWidget': MockQWidget,
    'QPushButton': MockQPushButton,
    'QTableWidget': MockQTableWidget,
    'QTableWidgetItem': MockQTableWidgetItem,
    'QVBoxLayout': MockQVBoxLayout,
    'QHBoxLayout': MockQHBoxLayout,
    'QLabel': MockQLabel,
    'QLineEdit': MockQLineEdit,
    'QComboBox': MockQComboBox,
    'QGroupBox': MockQGroupBox,
    'QHeaderView': MockQHeaderView
})()
sys.modules['PyQt6.QtCore'] = type('MockModule', (), {
    'Qt': MockQt,
    'pyqtSignal': lambda *args: lambda f: f,
    'QTimer': type('MockQTimer', (), {'setSingleShot': lambda self, x: None, 'timeout': lambda self: self, 'connect': lambda self, f: None, 'stop': lambda self: None, 'start': lambda self, x: None})
})()
sys.modules['PyQt6.QtGui'] = type('MockModule', (), {
    'QFont': type('MockQFont', (), {'Weight': type('MockWeight', (), {'Bold': 1})})
})()

# Test modules
modules_to_test = [
    ("administracion", "AdministracionView"),
    ("auditoria", "AuditoriaView"), 
    ("compras", "ComprasView"),
    ("configuracion", "ConfiguracionView"),
    ("herrajes", "HerrajesView"),
    ("inventario", "InventarioView"),
    ("logistica", "LogisticaView"),
    ("mantenimiento", "MantenimientoView"),
    ("obras", "ObrasView"),
    ("pedidos", "PedidosView"),
    ("usuarios", "UsuariosView"),
    ("vidrios", "VidriosView"),
]

print("Testing individual module imports:")
print("="*50)

for module_name, view_class in modules_to_test:
    try:
        module_path = f"rexus.modules.{module_name}.view"
        module = __import__(module_path, fromlist=[view_class])
        view_cls = getattr(module, view_class)
        print(f"{module_name:15} | {view_class:20} | [OK]")
        
        # Try to instantiate
        try:
            instance = view_cls()
            print(f"                 | Instance creation: [OK]")
        except Exception as e:
            print(f"                 | Instance creation: [WARN] {str(e)[:50]}")
        
    except Exception as e:
        print(f"{module_name:15} | {view_class:20} | [FAIL]")
        print(f"                 | Error: {str(e)[:80]}")

print("="*50)