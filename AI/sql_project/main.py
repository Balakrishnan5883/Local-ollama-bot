import sys
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                               QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLabel, QLineEdit, QPushButton, QTableView, QComboBox,
                               QDateEdit, QSpinBox, QTableWidget, QTableWidgetItem,
                               QMessageBox, QGroupBox, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QDate, QModelIndex
from PySide6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import os

class DatabaseManager:
    def __init__(self, db_path="employee_management.db"):
        self.db_path = db_path
        self.db = None
        self.init_database()
    
    def init_database(self):
        """Initialize the database connection"""
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_path)
        
        if not self.db.open():
            print("Error: Unable to open database")
            return False
            
        # Create tables if they don't exist
        self.create_tables()
        return True
    
    def create_tables(self):
        """Create tables if they don't exist"""
        query = QSqlQuery()
        
        # Create departments table
        query.exec_("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name VARCHAR(100) NOT NULL UNIQUE,
                manager_id INTEGER,
                budget DECIMAL(12, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create employees table
        query.exec_("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone VARCHAR(20),
                hire_date DATE NOT NULL,
                job_title VARCHAR(100),
                salary DECIMAL(10, 2),
                department_id INTEGER,
                manager_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(department_id),
                FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
            )
        """)
        
        # Create projects table
        query.exec_("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name VARCHAR(100) NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                budget DECIMAL(12, 2),
                status VARCHAR(20) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create employee_projects table
        query.exec_("""
            CREATE TABLE IF NOT EXISTS employee_projects (
                employee_id INTEGER,
                project_id INTEGER,
                assigned_date DATE NOT NULL,
                role VARCHAR(50),
                hours_worked DECIMAL(5, 2) DEFAULT 0,
                PRIMARY KEY (employee_id, project_id),
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        """)
        
        # Create views
        query.exec_("""
            CREATE VIEW IF NOT EXISTS employee_details AS
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.email,
                e.job_title,
                e.salary,
                d.department_name,
                m.first_name AS manager_first_name,
                m.last_name AS manager_last_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN employees m ON e.manager_id = m.employee_id;
        """)
        
        query.exec_("""
            CREATE VIEW IF NOT EXISTS project_assignments AS
            SELECT 
                ep.employee_id,
                e.first_name,
                e.last_name,
                ep.project_id,
                p.project_name,
                ep.assigned_date,
                ep.role,
                ep.hours_worked
            FROM employee_projects ep
            JOIN employees e ON ep.employee_id = e.employee_id
            JOIN projects p ON ep.project_id = p.project_id;
        """)

class EmployeeTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Employee form
        form_group = QGroupBox("Employee Form")
        form_layout = QFormLayout()
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDisplayFormat("yyyy-MM-dd")
        self.job_title_input = QLineEdit()
        self.salary_input = QSpinBox()
        self.salary_input.setMaximum(1000000)
        self.department_input = QComboBox()
        self.manager_input = QComboBox()
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Hire Date:", self.hire_date_input)
        form_layout.addRow("Job Title:", self.job_title_input)
        form_layout.addRow("Salary:", self.salary_input)
        form_layout.addRow("Department:", self.department_input)
        form_layout.addRow("Manager:", self.manager_input)
        
        form_group.setLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Employee")
        self.update_button = QPushButton("Update Employee")
        self.delete_button = QPushButton("Delete Employee")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_employee)
        self.update_button.clicked.connect(self.update_employee)
        self.delete_button.clicked.connect(self.delete_employee)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.employee_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.employee_table.clicked.connect(self.on_employee_selected)
        
        # Layout
        layout.addWidget(form_group, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.addWidget(self.employee_table, 2, 0)
        
        self.setLayout(layout)
        
        # Load department and manager data
        self.load_departments()
        self.load_managers()
    
    def load_departments(self):
        """Load departments into the department combo box"""
        self.department_input.clear()
        self.department_input.addItem("Select Department", 0)
        
        query = QSqlQuery()
        query.exec_("SELECT department_id, department_name FROM departments ORDER BY department_name")
        
        while query.next():
            dept_id = query.value(0)
            dept_name = query.value(1)
            self.department_input.addItem(dept_name, dept_id)
    
    def load_managers(self):
        """Load employees into the manager combo box"""
        self.manager_input.clear()
        self.manager_input.addItem("Select Manager", 0)
        
        query = QSqlQuery()
        query.exec_("SELECT employee_id, first_name, last_name FROM employees ORDER BY last_name")
        
        while query.next():
            emp_id = query.value(0)
            full_name = f"{query.value(1)} {query.value(2)}"
            self.manager_input.addItem(full_name, emp_id)
    
    def load_data(self):
        """Load employee data into the table"""
        self.employee_table.clear()
        self.employee_table.setColumnCount(9)
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Email", "Job Title", 
            "Salary", "Department", "Manager", "Hire Date"
        ])
        
        query = QSqlQuery()
        query.exec_("""
            SELECT e.employee_id, e.first_name, e.last_name, e.email, e.job_title,
                   e.salary, d.department_name, 
                   CASE WHEN m.first_name IS NOT NULL THEN m.first_name || ' ' || m.last_name ELSE 'None' END as manager_name,
                   e.hire_date
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            LEFT JOIN employees m ON e.manager_id = m.employee_id
            ORDER BY e.last_name
        """)
        
        self.employee_table.setRowCount(0)
        while query.next():
            row_position = self.employee_table.rowCount()
            self.employee_table.insertRow(row_position)
            
            for i in range(9):
                item = QTableWidgetItem(str(query.value(i)))
                self.employee_table.setItem(row_position, i, item)
        
        # Set column widths
        header = self.employee_table.horizontalHeader()
        for i in range(9):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def on_employee_selected(self, index):
        """Handle employee selection"""
        if index.isValid():
            row = index.row()
            # Get values from the selected row
            employee_id = self.employee_table.item(row, 0).text()
            
            # Load data into form
            self.first_name_input.setText(self.employee_table.item(row, 1).text())
            self.last_name_input.setText(self.employee_table.item(row, 2).text())
            self.email_input.setText(self.employee_table.item(row, 3).text())
            self.job_title_input.setText(self.employee_table.item(row, 4).text())
            self.salary_input.setValue(int(self.employee_table.item(row, 5).text()))
            
            # Set hire date
            hire_date = self.employee_table.item(row, 8).text()
            if hire_date:
                date_parts = hire_date.split('-')
                if len(date_parts) == 3:
                    qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                    self.hire_date_input.setDate(qdate)
            
            # Set department
            dept_name = self.employee_table.item(row, 6).text()
            dept_index = self.department_input.findText(dept_name)
            if dept_index >= 0:
                self.department_input.setCurrentIndex(dept_index)
            
            # Set manager
            manager_name = self.employee_table.item(row, 7).text()
            if manager_name != "None":
                manager_index = self.manager_input.findText(manager_name)
                if manager_index >= 0:
                    self.manager_input.setCurrentIndex(manager_index)
    
    def add_employee(self):
        """Add a new employee"""
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        hire_date = self.hire_date_input.date().toString("yyyy-MM-dd")
        job_title = self.job_title_input.text().strip()
        salary = self.salary_input.value()
        department_id = self.department_input.currentData()
        manager_id = self.manager_input.currentData()
        
        if not first_name or not last_name or not email:
            QMessageBox.warning(self, "Input Error", "First name, last name, and email are required.")
            return
        
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_title, salary, department_id, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(email)
        query.addBindValue(phone)
        query.addBindValue(hire_date)
        query.addBindValue(job_title)
        query.addBindValue(salary)
        query.addBindValue(department_id if department_id != 0 else None)
        query.addBindValue(manager_id if manager_id != 0 else None)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Employee added successfully!")
            self.clear_form()
            self.load_data()
            self.load_departments()
            self.load_managers()
        else:
            QMessageBox.critical(self, "Error", "Failed to add employee: " + query.lastError().text())
    
    def update_employee(self):
        """Update an existing employee"""
        # Get selected employee ID from form
        if not self.employee_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select an employee to update.")
            return
            
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        hire_date = self.hire_date_input.date().toString("yyyy-MM-dd")
        job_title = self.job_title_input.text().strip()
        salary = self.salary_input.value()
        department_id = self.department_input.currentData()
        manager_id = self.manager_input.currentData()
        
        if not first_name or not last_name or not email:
            QMessageBox.warning(self, "Input Error", "First name, last name, and email are required.")
            return
        
        # Get the selected employee ID from the table
        selected_row = self.employee_table.currentRow()
        employee_id = int(self.employee_table.item(selected_row, 0).text())
        
        query = QSqlQuery()
        query.prepare("""
            UPDATE employees 
            SET first_name=?, last_name=?, email=?, phone=?, hire_date=?, job_title=?, salary=?, department_id=?, manager_id=?
            WHERE employee_id=?
        """)
        query.addBindValue(first_name)
        query.addBindValue(last_name)
        query.addBindValue(email)
        query.addBindValue(phone)
        query.addBindValue(hire_date)
        query.addBindValue(job_title)
        query.addBindValue(salary)
        query.addBindValue(department_id if department_id != 0 else None)
        query.addBindValue(manager_id if manager_id != 0 else None)
        query.addBindValue(employee_id)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Employee updated successfully!")
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update employee: " + query.lastError().text())
    
    def delete_employee(self):
        """Delete an employee"""
        if not self.employee_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select an employee to delete.")
            return
            
        selected_row = self.employee_table.currentRow()
        employee_id = int(self.employee_table.item(selected_row, 0).text())
        employee_name = f"{self.employee_table.item(selected_row, 1).text()} {self.employee_table.item(selected_row, 2).text()}"
        
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete employee {employee_name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM employees WHERE employee_id=?")
            query.addBindValue(employee_id)
            
            if query.exec_():
                QMessageBox.information(self, "Success", "Employee deleted successfully!")
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete employee: " + query.lastError().text())
    
    def clear_form(self):
        """Clear the form inputs"""
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.hire_date_input.setDate(QDate.currentDate())
        self.job_title_input.clear()
        self.salary_input.setValue(0)
        self.department_input.setCurrentIndex(0)
        self.manager_input.setCurrentIndex(0)

class DepartmentTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Department form
        form_group = QGroupBox("Department Form")
        form_layout = QFormLayout()
        
        self.department_name_input = QLineEdit()
        self.manager_input = QComboBox()
        self.budget_input = QSpinBox()
        self.budget_input.setMaximum(10000000)
        
        form_layout.addRow("Department Name:", self.department_name_input)
        form_layout.addRow("Manager:", self.manager_input)
        form_layout.addRow("Budget:", self.budget_input)
        
        form_group.setLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Department")
        self.update_button = QPushButton("Update Department")
        self.delete_button = QPushButton("Delete Department")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_department)
        self.update_button.clicked.connect(self.update_department)
        self.delete_button.clicked.connect(self.delete_department)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Department table
        self.department_table = QTableWidget()
        self.department_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.department_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.department_table.clicked.connect(self.on_department_selected)
        
        # Layout
        layout.addWidget(form_group, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.addWidget(self.department_table, 2, 0)
        
        self.setLayout(layout)
        
        # Load manager data
        self.load_managers()
    
    def load_managers(self):
        """Load employees into the manager combo box"""
        self.manager_input.clear()
        self.manager_input.addItem("Select Manager", 0)
        
        query = QSqlQuery()
        query.exec_("SELECT employee_id, first_name, last_name FROM employees ORDER BY last_name")
        
        while query.next():
            emp_id = query.value(0)
            full_name = f"{query.value(1)} {query.value(2)}"
            self.manager_input.addItem(full_name, emp_id)
    
    def load_data(self):
        """Load department data into the table"""
        self.department_table.clear()
        self.department_table.setColumnCount(5)
        self.department_table.setHorizontalHeaderLabels([
            "ID", "Department Name", "Manager", "Budget", "Created At"
        ])
        
        query = QSqlQuery()
        query.exec_("""
            SELECT d.department_id, d.department_name,
                   CASE WHEN m.first_name IS NOT NULL THEN m.first_name || ' ' || m.last_name ELSE 'None' END as manager_name,
                   d.budget, d.created_at
            FROM departments d
            LEFT JOIN employees m ON d.manager_id = m.employee_id
            ORDER BY d.department_name
        """)
        
        self.department_table.setRowCount(0)
        while query.next():
            row_position = self.department_table.rowCount()
            self.department_table.insertRow(row_position)
            
            for i in range(5):
                item = QTableWidgetItem(str(query.value(i)))
                self.department_table.setItem(row_position, i, item)
        
        # Set column widths
        header = self.department_table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def on_department_selected(self, index):
        """Handle department selection"""
        if index.isValid():
            row = index.row()
            # Get values from the selected row
            department_id = self.department_table.item(row, 0).text()
            
            # Load data into form
            self.department_name_input.setText(self.department_table.item(row, 1).text())
            self.budget_input.setValue(int(self.department_table.item(row, 3).text()))
            
            # Set manager
            manager_name = self.department_table.item(row, 2).text()
            if manager_name != "None":
                manager_index = self.manager_input.findText(manager_name)
                if manager_index >= 0:
                    self.manager_input.setCurrentIndex(manager_index)
    
    def add_department(self):
        """Add a new department"""
        department_name = self.department_name_input.text().strip()
        budget = self.budget_input.value()
        manager_id = self.manager_input.currentData()
        
        if not department_name:
            QMessageBox.warning(self, "Input Error", "Department name is required.")
            return
        
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO departments (department_name, budget, manager_id)
            VALUES (?, ?, ?)
        """)
        query.addBindValue(department_name)
        query.addBindValue(budget)
        query.addBindValue(manager_id if manager_id != 0 else None)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Department added successfully!")
            self.clear_form()
            self.load_data()
            self.load_managers()
        else:
            QMessageBox.critical(self, "Error", "Failed to add department: " + query.lastError().text())
    
    def update_department(self):
        """Update an existing department"""
        if not self.department_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select a department to update.")
            return
            
        department_name = self.department_name_input.text().strip()
        budget = self.budget_input.value()
        manager_id = self.manager_input.currentData()
        
        if not department_name:
            QMessageBox.warning(self, "Input Error", "Department name is required.")
            return
        
        # Get the selected department ID from the table
        selected_row = self.department_table.currentRow()
        department_id = int(self.department_table.item(selected_row, 0).text())
        
        query = QSqlQuery()
        query.prepare("""
            UPDATE departments 
            SET department_name=?, budget=?, manager_id=?
            WHERE department_id=?
        """)
        query.addBindValue(department_name)
        query.addBindValue(budget)
        query.addBindValue(manager_id if manager_id != 0 else None)
        query.addBindValue(department_id)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Department updated successfully!")
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update department: " + query.lastError().text())
    
    def delete_department(self):
        """Delete a department"""
        if not self.department_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select a department to delete.")
            return
            
        selected_row = self.department_table.currentRow()
        department_id = int(self.department_table.item(selected_row, 0).text())
        department_name = self.department_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete department {department_name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM departments WHERE department_id=?")
            query.addBindValue(department_id)
            
            if query.exec_():
                QMessageBox.information(self, "Success", "Department deleted successfully!")
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete department: " + query.lastError().text())
    
    def clear_form(self):
        """Clear the form inputs"""
        self.department_name_input.clear()
        self.budget_input.setValue(0)
        self.manager_input.setCurrentIndex(0)

class ProjectTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Project form
        form_group = QGroupBox("Project Form")
        form_layout = QFormLayout()
        
        self.project_name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.budget_input = QSpinBox()
        self.budget_input.setMaximum(10000000)
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Completed", "On Hold", "Cancelled"])
        
        form_layout.addRow("Project Name:", self.project_name_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        form_layout.addRow("Budget:", self.budget_input)
        form_layout.addRow("Status:", self.status_input)
        
        form_group.setLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Project")
        self.update_button = QPushButton("Update Project")
        self.delete_button = QPushButton("Delete Project")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_project)
        self.update_button.clicked.connect(self.update_project)
        self.delete_button.clicked.connect(self.delete_project)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Project table
        self.project_table = QTableWidget()
        self.project_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.project_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.project_table.clicked.connect(self.on_project_selected)
        
        # Layout
        layout.addWidget(form_group, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.addWidget(self.project_table, 2, 0)
        
        self.setLayout(layout)
    
    def load_data(self):
        """Load project data into the table"""
        self.project_table.clear()
        self.project_table.setColumnCount(8)
        self.project_table.setHorizontalHeaderLabels([
            "ID", "Project Name", "Description", "Start Date", "End Date", 
            "Budget", "Status", "Created At"
        ])
        
        query = QSqlQuery()
        query.exec_("""
            SELECT project_id, project_name, description, start_date, end_date, 
                   budget, status, created_at
            FROM projects
            ORDER BY project_name
        """)
        
        self.project_table.setRowCount(0)
        while query.next():
            row_position = self.project_table.rowCount()
            self.project_table.insertRow(row_position)
            
            for i in range(8):
                item = QTableWidgetItem(str(query.value(i)))
                self.project_table.setItem(row_position, i, item)
        
        # Set column widths
        header = self.project_table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def on_project_selected(self, index):
        """Handle project selection"""
        if index.isValid():
            row = index.row()
            # Get values from the selected row
            project_id = self.project_table.item(row, 0).text()
            
            # Load data into form
            self.project_name_input.setText(self.project_table.item(row, 1).text())
            self.description_input.setText(self.project_table.item(row, 2).text())
            
            # Set dates
            start_date = self.project_table.item(row, 3).text()
            if start_date:
                date_parts = start_date.split('-')
                if len(date_parts) == 3:
                    qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                    self.start_date_input.setDate(qdate)
            
            end_date = self.project_table.item(row, 4).text()
            if end_date:
                date_parts = end_date.split('-')
                if len(date_parts) == 3:
                    qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                    self.end_date_input.setDate(qdate)
            
            self.budget_input.setValue(int(self.project_table.item(row, 5).text()))
            self.status_input.setCurrentText(self.project_table.item(row, 6).text())
    
    def add_project(self):
        """Add a new project"""
        project_name = self.project_name_input.text().strip()
        description = self.description_input.text().strip()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        budget = self.budget_input.value()
        status = self.status_input.currentText()
        
        if not project_name:
            QMessageBox.warning(self, "Input Error", "Project name is required.")
            return
        
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO projects (project_name, description, start_date, end_date, budget, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """)
        query.addBindValue(project_name)
        query.addBindValue(description)
        query.addBindValue(start_date)
        query.addBindValue(end_date)
        query.addBindValue(budget)
        query.addBindValue(status)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Project added successfully!")
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to add project: " + query.lastError().text())
    
    def update_project(self):
        """Update an existing project"""
        if not self.project_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select a project to update.")
            return
            
        project_name = self.project_name_input.text().strip()
        description = self.description_input.text().strip()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")
        budget = self.budget_input.value()
        status = self.status_input.currentText()
        
        if not project_name:
            QMessageBox.warning(self, "Input Error", "Project name is required.")
            return
        
        # Get the selected project ID from the table
        selected_row = self.project_table.currentRow()
        project_id = int(self.project_table.item(selected_row, 0).text())
        
        query = QSqlQuery()
        query.prepare("""
            UPDATE projects 
            SET project_name=?, description=?, start_date=?, end_date=?, budget=?, status=?
            WHERE project_id=?
        """)
        query.addBindValue(project_name)
        query.addBindValue(description)
        query.addBindValue(start_date)
        query.addBindValue(end_date)
        query.addBindValue(budget)
        query.addBindValue(status)
        query.addBindValue(project_id)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Project updated successfully!")
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update project: " + query.lastError().text())
    
    def delete_project(self):
        """Delete a project"""
        if not self.project_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select a project to delete.")
            return
            
        selected_row = self.project_table.currentRow()
        project_id = int(self.project_table.item(selected_row, 0).text())
        project_name = self.project_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete project {project_name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM projects WHERE project_id=?")
            query.addBindValue(project_id)
            
            if query.exec_():
                QMessageBox.information(self, "Success", "Project deleted successfully!")
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete project: " + query.lastError().text())
    
    def clear_form(self):
        """Clear the form inputs"""
        self.project_name_input.clear()
        self.description_input.clear()
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())
        self.budget_input.setValue(0)
        self.status_input.setCurrentIndex(0)

class EmployeeProjectTab(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Employee-Project form
        form_group = QGroupBox("Employee-Project Assignment")
        form_layout = QFormLayout()
        
        self.employee_input = QComboBox()
        self.project_input = QComboBox()
        self.assigned_date_input = QDateEdit()
        self.assigned_date_input.setCalendarPopup(True)
        self.assigned_date_input.setDisplayFormat("yyyy-MM-dd")
        self.role_input = QLineEdit()
        self.hours_worked_input = QSpinBox()
        self.hours_worked_input.setMaximum(1000)
        
        form_layout.addRow("Employee:", self.employee_input)
        form_layout.addRow("Project:", self.project_input)
        form_layout.addRow("Assigned Date:", self.assigned_date_input)
        form_layout.addRow("Role:", self.role_input)
        form_layout.addRow("Hours Worked:", self.hours_worked_input)
        
        form_group.setLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Assign Employee to Project")
        self.update_button = QPushButton("Update Assignment")
        self.delete_button = QPushButton("Delete Assignment")
        self.clear_button = QPushButton("Clear Form")
        
        self.add_button.clicked.connect(self.add_assignment)
        self.update_button.clicked.connect(self.update_assignment)
        self.delete_button.clicked.connect(self.delete_assignment)
        self.clear_button.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        
        # Assignment table
        self.assignment_table = QTableWidget()
        self.assignment_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.assignment_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.assignment_table.clicked.connect(self.on_assignment_selected)
        
        # Layout
        layout.addWidget(form_group, 0, 0)
        layout.addLayout(button_layout, 1, 0)
        layout.addWidget(self.assignment_table, 2, 0)
        
        self.setLayout(layout)
        
        # Load employee and project data
        self.load_employees()
        self.load_projects()
    
    def load_employees(self):
        """Load employees into the employee combo box"""
        self.employee_input.clear()
        self.employee_input.addItem("Select Employee", 0)
        
        query = QSqlQuery()
        query.exec_("SELECT employee_id, first_name, last_name FROM employees ORDER BY last_name")
        
        while query.next():
            emp_id = query.value(0)
            full_name = f"{query.value(1)} {query.value(2)}"
            self.employee_input.addItem(full_name, emp_id)
    
    def load_projects(self):
        """Load projects into the project combo box"""
        self.project_input.clear()
        self.project_input.addItem("Select Project", 0)
        
        query = QSqlQuery()
        query.exec_("SELECT project_id, project_name FROM projects ORDER BY project_name")
        
        while query.next():
            proj_id = query.value(0)
            proj_name = query.value(1)
            self.project_input.addItem(proj_name, proj_id)
    
    def load_data(self):
        """Load assignment data into the table"""
        self.assignment_table.clear()
        self.assignment_table.setColumnCount(7)
        self.assignment_table.setHorizontalHeaderLabels([
            "Employee ID", "Employee Name", "Project ID", "Project Name", 
            "Assigned Date", "Role", "Hours Worked"
        ])
        
        query = QSqlQuery()
        query.exec_("""
            SELECT ep.employee_id, e.first_name || ' ' || e.last_name as employee_name,
                   ep.project_id, p.project_name, ep.assigned_date, ep.role, ep.hours_worked
            FROM employee_projects ep
            JOIN employees e ON ep.employee_id = e.employee_id
            JOIN projects p ON ep.project_id = p.project_id
            ORDER BY e.last_name, p.project_name
        """)
        
        self.assignment_table.setRowCount(0)
        while query.next():
            row_position = self.assignment_table.rowCount()
            self.assignment_table.insertRow(row_position)
            
            for i in range(7):
                item = QTableWidgetItem(str(query.value(i)))
                self.assignment_table.setItem(row_position, i, item)
        
        # Set column widths
        header = self.assignment_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    
    def on_assignment_selected(self, index):
        """Handle assignment selection"""
        if index.isValid():
            row = index.row()
            # Get values from the selected row
            employee_id = self.assignment_table.item(row, 0).text()
            project_id = self.assignment_table.item(row, 2).text()
            
            # Load data into form
            employee_name = self.assignment_table.item(row, 1).text()
            project_name = self.assignment_table.item(row, 3).text()
            
            # Set employee
            employee_index = self.employee_input.findText(employee_name)
            if employee_index >= 0:
                self.employee_input.setCurrentIndex(employee_index)
            
            # Set project
            project_index = self.project_input.findText(project_name)
            if project_index >= 0:
                self.project_input.setCurrentIndex(project_index)
            
            # Set dates
            assigned_date = self.assignment_table.item(row, 4).text()
            if assigned_date:
                date_parts = assigned_date.split('-')
                if len(date_parts) == 3:
                    qdate = QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                    self.assigned_date_input.setDate(qdate)
            
            # Set role and hours
            self.role_input.setText(self.assignment_table.item(row, 5).text())
            self.hours_worked_input.setValue(int(self.assignment_table.item(row, 6).text()))
    
    def add_assignment(self):
        """Add a new employee-project assignment"""
        employee_id = self.employee_input.currentData()
        project_id = self.project_input.currentData()
        assigned_date = self.assigned_date_input.date().toString("yyyy-MM-dd")
        role = self.role_input.text().strip()
        hours_worked = self.hours_worked_input.value()
        
        if employee_id == 0 or project_id == 0:
            QMessageBox.warning(self, "Input Error", "Please select both employee and project.")
            return
        
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO employee_projects (employee_id, project_id, assigned_date, role, hours_worked)
            VALUES (?, ?, ?, ?, ?)
        """)
        query.addBindValue(employee_id)
        query.addBindValue(project_id)
        query.addBindValue(assigned_date)
        query.addBindValue(role)
        query.addBindValue(hours_worked)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Assignment added successfully!")
            self.clear_form()
            self.load_data()
            self.load_employees()
            self.load_projects()
        else:
            QMessageBox.critical(self, "Error", "Failed to add assignment: " + query.lastError().text())
    
    def update_assignment(self):
        """Update an existing assignment"""
        if not self.assignment_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select an assignment to update.")
            return
            
        employee_id = self.employee_input.currentData()
        project_id = self.project_input.currentData()
        assigned_date = self.assigned_date_input.date().toString("yyyy-MM-dd")
        role = self.role_input.text().strip()
        hours_worked = self.hours_worked_input.value()
        
        if employee_id == 0 or project_id == 0:
            QMessageBox.warning(self, "Input Error", "Please select both employee and project.")
            return
        
        # Get the selected assignment (using employee_id and project_id)
        selected_row = self.assignment_table.currentRow()
        # Note: We'll update based on the current selection, but since it's a composite key,
        # we'll need to identify it by the row
        # For simplicity, we'll just update the current values
        
        # Since we're updating a composite key, we'll delete and re-add
        # But for this implementation, we'll just update the values
        query = QSqlQuery()
        query.prepare("""
            UPDATE employee_projects 
            SET assigned_date=?, role=?, hours_worked=?
            WHERE employee_id=? AND project_id=?
        """)
        query.addBindValue(assigned_date)
        query.addBindValue(role)
        query.addBindValue(hours_worked)
        query.addBindValue(employee_id)
        query.addBindValue(project_id)
        
        if query.exec_():
            QMessageBox.information(self, "Success", "Assignment updated successfully!")
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to update assignment: " + query.lastError().text())
    
    def delete_assignment(self):
        """Delete an assignment"""
        if not self.assignment_table.currentRow() >= 0:
            QMessageBox.warning(self, "Selection Error", "Please select an assignment to delete.")
            return
            
        selected_row = self.assignment_table.currentRow()
        
        # Get employee and project IDs
        employee_id = int(self.assignment_table.item(selected_row, 0).text())
        project_id = int(self.assignment_table.item(selected_row, 2).text())
        
        # Get names for confirmation
        employee_name = self.assignment_table.item(selected_row, 1).text()
        project_name = self.assignment_table.item(selected_row, 3).text()
        
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete assignment for {employee_name} on project {project_name}?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = QSqlQuery()
            query.prepare("DELETE FROM employee_projects WHERE employee_id=? AND project_id=?")
            query.addBindValue(employee_id)
            query.addBindValue(project_id)
            
            if query.exec_():
                QMessageBox.information(self, "Success", "Assignment deleted successfully!")
                self.clear_form()
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete assignment: " + query.lastError().text())
    
    def clear_form(self):
        """Clear the form inputs"""
        self.employee_input.setCurrentIndex(0)
        self.project_input.setCurrentIndex(0)
        self.assigned_date_input.setDate(QDate.currentDate())
        self.role_input.clear()
        self.hours_worked_input.setValue(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.employee_tab = EmployeeTab(self.db_manager)
        self.department_tab = DepartmentTab(self.db_manager)
        self.project_tab = ProjectTab(self.db_manager)
        self.employee_project_tab = EmployeeProjectTab(self.db_manager)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.employee_tab, "Employees")
        self.tabs.addTab(self.department_tab, "Departments")
        self.tabs.addTab(self.project_tab, "Projects")
        self.tabs.addTab(self.employee_project_tab, "Employee-Projects")
        
        # Set central widget
        self.setCentralWidget(self.tabs)
        
        # Create status bar
        self.statusBar().showMessage("Ready")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())