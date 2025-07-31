"""
UI Feedback System - Rexus.app
Enhanced visual feedback and loading indicators for better UX.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QFrame, QPushButton, QApplication, QDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter
import time
from typing import Optional, Callable, Any
from enum import Enum

class FeedbackType(Enum):
    """Types of feedback messages."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"

class LoadingIndicator(QWidget):
    """
    Animated loading indicator widget.
    """
    
    def __init__(self, message: str = "Cargando...", parent=None):
        super().__init__(parent)
        self.message = message
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_step = 0
        
    def setup_ui(self):
        """Setup the loading indicator UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Loading animation
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 10px;
                text-align: center;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0.5, x2: 1, y2: 0.5,
                    stop: 0 #3498db, stop: 1 #2980b9
                );
                border-radius: 8px;
            }
        """)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px;
            }
        """)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.message_label)
        
        # Style the widget
        self.setStyleSheet("""
            LoadingIndicator {
                background-color: rgba(248, 249, 250, 0.95);
                border: 2px solid #bdc3c7;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
    def start(self):
        """Start the loading animation."""
        self.timer.start(100)
        self.show()
        
    def stop(self):
        """Stop the loading animation."""
        self.timer.stop()
        self.hide()
        
    def update_message(self, message: str):
        """Update the loading message."""
        self.message = message
        self.message_label.setText(message)
        
    def update_animation(self):
        """Update animation step."""
        self.animation_step = (self.animation_step + 1) % 10

class ToastNotification(QWidget):
    """
    Toast-style notification widget.
    """
    
    def __init__(self, message: str, feedback_type: FeedbackType, 
                 duration: int = 3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.feedback_type = feedback_type
        self.duration = duration
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        """Setup the toast notification UI."""
        layout = QHBoxLayout(self)
        
        # Icon based on type
        icon_label = QLabel()
        icon_text = self.get_icon_for_type()
        icon_label.setText(icon_text)
        icon_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Message label
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 13px; font-weight: 500;")
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        # Style based on type
        self.setStyleSheet(self.get_style_for_type())
        self.setFixedHeight(60)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
    def get_icon_for_type(self) -> str:
        """Get icon text for feedback type."""
        icons = {
            FeedbackType.SUCCESS: "✅",
            FeedbackType.ERROR: "❌",
            FeedbackType.WARNING: "⚠️",
            FeedbackType.INFO: "ℹ️",
            FeedbackType.LOADING: "⏳"
        }
        return icons.get(self.feedback_type, "ℹ️")
    
    def get_style_for_type(self) -> str:
        """Get stylesheet for feedback type."""
        styles = {
            FeedbackType.SUCCESS: """
                ToastNotification {
                    background-color: #d4edda;
                    border: 2px solid #c3e6cb;
                    border-left: 5px solid #28a745;
                    border-radius: 8px;
                    padding: 10px;
                    color: #155724;
                }
            """,
            FeedbackType.ERROR: """
                ToastNotification {
                    background-color: #f8d7da;
                    border: 2px solid #f5c6cb;
                    border-left: 5px solid #dc3545;
                    border-radius: 8px;
                    padding: 10px;
                    color: #721c24;
                }
            """,
            FeedbackType.WARNING: """
                ToastNotification {
                    background-color: #fff3cd;
                    border: 2px solid #ffeaa7;
                    border-left: 5px solid #ffc107;
                    border-radius: 8px;
                    padding: 10px;
                    color: #856404;
                }
            """,
            FeedbackType.INFO: """
                ToastNotification {
                    background-color: #d1ecf1;
                    border: 2px solid #bee5eb;
                    border-left: 5px solid #17a2b8;
                    border-radius: 8px;
                    padding: 10px;
                    color: #0c5460;
                }
            """,
            FeedbackType.LOADING: """
                ToastNotification {
                    background-color: #e2e3e5;
                    border: 2px solid #d6d8db;
                    border-left: 5px solid #6c757d;
                    border-radius: 8px;
                    padding: 10px;
                    color: #383d41;
                }
            """
        }
        return styles.get(self.feedback_type, styles[FeedbackType.INFO])
    
    def setup_animation(self):
        """Setup fade in/out animations."""
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out_animation.finished.connect(self.close)
        
    def show_toast(self):
        """Show the toast notification with animation."""
        self.show()
        self.fade_in_animation.start()
        
        # Auto-hide after duration
        QTimer.singleShot(self.duration, self.hide_toast)
        
    def hide_toast(self):
        """Hide the toast notification with animation."""
        self.fade_out_animation.start()

class StatusBar(QWidget):
    """
    Enhanced status bar with progress and messages.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Status message
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        
        layout.addWidget(self.status_label, 1)
        layout.addWidget(self.progress_bar)
        
        # Style the status bar
        self.setStyleSheet("""
            StatusBar {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
            }
        """)
        
    def show_message(self, message: str, timeout: int = 0):
        """
        Show status message.
        
        Args:
            message: Message to display
            timeout: Auto-clear timeout in milliseconds (0 = no timeout)
        """
        self.status_label.setText(message)
        
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Listo"))
    
    def show_progress(self, message: str = "Procesando...", maximum: int = 0):
        """
        Show progress bar.
        
        Args:
            message: Progress message
            maximum: Maximum value (0 for indeterminate)
        """
        self.status_label.setText(message)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
    def update_progress(self, value: int, message: str = None):
        """
        Update progress value.
        
        Args:
            value: Current progress value
            message: Optional message update
        """
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
            
    def hide_progress(self, message: str = "Completado"):
        """
        Hide progress bar.
        
        Args:
            message: Final message
        """
        self.progress_bar.setVisible(False)
        self.show_message(message, 3000)

class BackgroundTask(QThread):
    """
    Background task with progress reporting.
    """
    progress_updated = pyqtSignal(int, str)
    task_completed = pyqtSignal(object)
    task_failed = pyqtSignal(str)
    
    def __init__(self, task_function: Callable, *args, **kwargs):
        super().__init__()
        self.task_function = task_function
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        """Execute the background task."""
        try:
            result = self.task_function(*self.args, **self.kwargs)
            self.task_completed.emit(result)
        except Exception as e:
            self.task_failed.emit(str(e))

class FeedbackManager:
    """
    Central manager for UI feedback.
    """
    
    def __init__(self, parent_widget: QWidget = None):
        self.parent_widget = parent_widget
        self.active_toasts = []
        
    def show_success(self, message: str, duration: int = 3000):
        """Show success notification."""
        self._show_toast(message, FeedbackType.SUCCESS, duration)
        
    def show_error(self, message: str, duration: int = 5000):
        """Show error notification."""
        self._show_toast(message, FeedbackType.ERROR, duration)
        
    def show_warning(self, message: str, duration: int = 4000):
        """Show warning notification."""
        self._show_toast(message, FeedbackType.WARNING, duration)
        
    def show_info(self, message: str, duration: int = 3000):
        """Show info notification."""
        self._show_toast(message, FeedbackType.INFO, duration)
        
    def show_loading(self, message: str = "Cargando...") -> LoadingIndicator:
        """
        Show loading indicator.
        
        Args:
            message: Loading message
            
        Returns:
            LoadingIndicator instance
        """
        loading_indicator = LoadingIndicator(message, self.parent_widget)
        loading_indicator.start()
        return loading_indicator
        
    def _show_toast(self, message: str, feedback_type: FeedbackType, duration: int):
        """Show toast notification."""
        toast = ToastNotification(message, feedback_type, duration, self.parent_widget)
        
        # Position toast
        if self.parent_widget:
            parent_geometry = self.parent_widget.geometry()
            toast_width = 400
            toast_x = parent_geometry.x() + parent_geometry.width() - toast_width - 20
            toast_y = parent_geometry.y() + 20 + (len(self.active_toasts) * 70)
            toast.setGeometry(toast_x, toast_y, toast_width, 60)
        
        # Show toast
        toast.show_toast()
        self.active_toasts.append(toast)
        
        # Remove from active list when closed
        QTimer.singleShot(duration + 500, lambda: self._remove_toast(toast))
        
    def _remove_toast(self, toast: ToastNotification):
        """Remove toast from active list."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)

class ConfirmationDialog(QDialog):
    """
    Enhanced confirmation dialog with better styling.
    """
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setup_ui(message)
        
    def setup_ui(self, message: str):
        """Setup confirmation dialog UI."""
        layout = QVBoxLayout(self)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 20px;
                color: #2c3e50;
            }
        """)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        self.confirm_button = QPushButton("Confirmar")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.confirm_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.confirm_button)
        
        layout.addWidget(message_label)
        layout.addLayout(button_layout)
        
        # Style dialog
        self.setStyleSheet("""
            ConfirmationDialog {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
            }
        """)
        self.setFixedSize(400, 200)

# Global feedback manager
feedback_manager = FeedbackManager()

def show_success(message: str, duration: int = 3000):
    """Show success notification."""
    feedback_manager.show_success(message, duration)

def show_error(message: str, duration: int = 5000):
    """Show error notification."""
    feedback_manager.show_error(message, duration)

def show_warning(message: str, duration: int = 4000):
    """Show warning notification."""
    feedback_manager.show_warning(message, duration)

def show_info(message: str, duration: int = 3000):
    """Show info notification."""
    feedback_manager.show_info(message, duration)

def show_loading(message: str = "Cargando...") -> LoadingIndicator:
    """Show loading indicator."""
    return feedback_manager.show_loading(message)