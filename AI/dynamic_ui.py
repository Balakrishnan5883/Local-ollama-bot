import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, 
                               QLineEdit, QLabel, QPushButton, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt

class DynamicUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic UI with Checkboxes and Text Boxes")
        self.setGeometry(100, 100, 600, 500)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Dynamic UI with Checkboxes and Text Boxes")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Selection group
        selection_group = QGroupBox("Select Options")
        selection_layout = QVBoxLayout()
        
        # Checkboxes for selection
        self.checkbox1 = QCheckBox("Enable Text Input 1")
        self.checkbox2 = QCheckBox("Enable Text Input 2")
        self.checkbox3 = QCheckBox("Enable Text Input 3")
        self.checkbox4 = QCheckBox("Enable Text Input 4")
        
        # Style checkboxes
        checkboxes = [self.checkbox1, self.checkbox2, self.checkbox3, self.checkbox4]
        for checkbox in checkboxes:
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #34495e;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator::unchecked {
                    border: 2px solid #3498db;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator::checked {
                    border: 2px solid #27ae60;
                    background-color: #27ae60;
                    image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>');
                }
            """)
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            selection_layout.addWidget(checkbox)
        
        selection_group.setLayout(selection_layout)
        main_layout.addWidget(selection_group)
        
        # Scroll area for dynamic widgets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # Clear button
        clear_button = QPushButton("Clear All")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_button.clicked.connect(self.clear_all)
        main_layout.addWidget(clear_button)
        
        self.setLayout(main_layout)
        
        # Initialize dynamic widgets container
        self.dynamic_widgets = []
        
    def on_checkbox_changed(self, state):
        # Get the checkbox that triggered the event
        sender = self.sender()
        
        # Create or remove dynamic widgets based on checkbox state
        if sender == self.checkbox1:
            self.create_dynamic_widget(1, "Input 1", "Enter your text here...")
        elif sender == self.checkbox2:
            self.create_dynamic_widget(2, "Input 2", "Enter your text here...")
        elif sender == self.checkbox3:
            self.create_dynamic_widget(3, "Input 3", "Enter your text here...")
        elif sender == self.checkbox4:
            self.create_dynamic_widget(4, "Input 4", "Enter your text here...")
    
    def create_dynamic_widget(self, widget_id, label_text, placeholder_text):
        # Check if widget already exists
        existing_widget = next((w for w in self.dynamic_widgets if w['id'] == widget_id), None)
        
        if existing_widget:
            # If widget exists and checkbox is unchecked, remove it
            if not existing_widget['checkbox'].isChecked():
                self.scroll_layout.removeWidget(existing_widget['widget'])
                existing_widget['widget'].deleteLater()
                self.dynamic_widgets.remove(existing_widget)
        else:
            # Create new widget if checkbox is checked
            if self.sender().isChecked():
                # Create widget container
                widget_container = QWidget()
                container_layout = QVBoxLayout()
                container_layout.setSpacing(5)
                container_layout.setContentsMargins(0, 0, 0, 0)
                
                # Label
                label = QLabel(label_text)
                label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        font-weight: bold;
                        color: #2c3e50;
                    }
                """)
                
                # Text input
                text_input = QLineEdit()
                text_input.setPlaceholderText(placeholder_text)
                text_input.setStyleSheet("""
                    QLineEdit {
                        padding: 8px;
                        border: 2px solid #bdc3c7;
                        border-radius: 5px;
                        font-size: 14px;
                        background-color: white;
                    }
                    QLineEdit:focus {
                        border: 2px solid #3498db;
                    }
                """)
                
                # Add to layout
                container_layout.addWidget(label)
                container_layout.addWidget(text_input)
                widget_container.setLayout(container_layout)
                
                # Store reference
                dynamic_info = {
                    'id': widget_id,
                    'checkbox': self.sender(),
                    'widget': widget_container,
                    'input': text_input
                }
                self.dynamic_widgets.append(dynamic_info)
                
                # Add to scroll layout
                self.scroll_layout.addWidget(widget_container)
    
    def clear_all(self):
        # Uncheck all checkboxes
        for checkbox in [self.checkbox1, self.checkbox2, self.checkbox3, self.checkbox4]:
            checkbox.setChecked(False)
        
        # Remove all dynamic widgets
        for widget_info in self.dynamic_widgets:
            self.scroll_layout.removeWidget(widget_info['widget'])
            widget_info['widget'].deleteLater()
        
        self.dynamic_widgets.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set global stylesheet for a modern look
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #ecf0f1;
        }
        QGroupBox {
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subline-color: #3498db;
            margin-left: 10px;
            font-weight: bold;
            color: #2c3e50;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #34495e;
        }
    """)
    
    window = DynamicUI()
    window.show()
    sys.exit(app.exec())