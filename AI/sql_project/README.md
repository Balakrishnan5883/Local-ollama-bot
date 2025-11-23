# Employee Management System - SQL Project

## Overview

This project demonstrates a complete Employee Management System with a graphical user interface built using PySide6. The system allows users to perform all CRUD (Create, Read, Update, Delete) operations on employees, departments, projects, and employee-project assignments.

## Features

- **Employee Management**: Add, update, delete, and view employees with full details
- **Department Management**: Manage departments including budget and manager assignments
- **Project Management**: Create and track projects with status, dates, and budgets
- **Employee-Project Assignments**: Assign employees to projects with roles and hours worked
- **Data Validation**: Input validation and error handling
- **User-Friendly Interface**: Intuitive tabbed interface with forms and data tables

## Database Schema

The system uses a relational database with the following entities:

1. **Departments**: 
   - department_id (Primary Key)
   - department_name
   - manager_id (Foreign Key)
   - budget
   - created_at
   - updated_at

2. **Employees**:
   - employee_id (Primary Key)
   - first_name
   - last_name
   - email (Unique)
   - phone
   - hire_date
   - job_title
   - salary
   - department_id (Foreign Key)
   - manager_id (Foreign Key)
   - created_at
   - updated_at

3. **Projects**:
   - project_id (Primary Key)
   - project_name
   - description
   - start_date
   - end_date
   - budget
   - status
   - created_at
   - updated_at

4. **Employee-Projects** (Junction Table):
   - employee_id (Primary Key, Foreign Key)
   - project_id (Primary Key, Foreign Key)
   - assigned_date
   - role
   - hours_worked

## Requirements

- Python 3.6 or higher
- PySide6
- SQLite3 (included with Python)

## Installation

1. Ensure you have Python 3.6 or higher installed
2. Install PySide6:
   ```bash
   pip install PySide6
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

The application has four main tabs:

1. **Employees Tab**: Manage employee records with full details
2. **Departments Tab**: Manage departments including budget and manager assignments
3. **Projects Tab**: Create and track projects with status and dates
4. **Employee-Projects Tab**: Assign employees to projects with roles and hours worked

Each tab provides full CRUD functionality:
- **Add**: Fill in the form and click "Add"
- **Update**: Select a record, modify the form, and click "Update"
- **Delete**: Select a record and click "Delete" (confirmation required)
- **View**: All records are displayed in the table

## Database Structure

The application automatically creates the necessary database tables and views when run. The database schema includes:

- Primary and foreign key constraints
- Indexes for performance
- Views for common queries
- Triggers to update timestamps
- Functions for calculations

## Design Considerations

- **User Experience**: Intuitive tabbed interface with clear forms
- **Data Integrity**: Proper constraints and validation
- **Performance**: Indexes on frequently queried columns
- **Scalability**: Modular design for easy extension
- **Error Handling**: Comprehensive error messages and validation

## Future Enhancements

- Add search and filtering capabilities
- Implement data export functionality
- Add user authentication
- Include reporting features
- Implement advanced data visualization
- Add data import functionality from CSV