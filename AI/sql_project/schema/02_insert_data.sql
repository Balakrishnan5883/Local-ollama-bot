-- Insert sample departments
INSERT INTO departments (department_name, budget) VALUES
('Human Resources', 500000.00),
('Engineering', 1500000.00),
('Marketing', 750000.00),
('Sales', 1000000.00),
('Finance', 600000.00);

-- Insert sample employees
INSERT INTO employees (first_name, last_name, email, phone, hire_date, job_title, salary, department_id) VALUES
('John', 'Doe', 'john.doe@company.com', '555-0101', '2020-01-15', 'HR Manager', 75000.00, 1),
('Jane', 'Smith', 'jane.smith@company.com', '555-0102', '2019-03-22', 'Software Engineer', 85000.00, 2),
('Robert', 'Johnson', 'robert.johnson@company.com', '555-0103', '2021-06-10', 'Marketing Specialist', 60000.00, 3),
('Emily', 'Williams', 'emily.williams@company.com', '555-0104', '2020-11-05', 'Sales Representative', 55000.00, 4),
('Michael', 'Brown', 'michael.brown@company.com', '555-0105', '2018-08-14', 'Financial Analyst', 70000.00, 5),
('Sarah', 'Davis', 'sarah.davis@company.com', '555-0106', '2021-02-28', 'Software Engineer', 90000.00, 2),
('David', 'Miller', 'david.miller@company.com', '555-0107', '2020-09-12', 'Marketing Manager', 80000.00, 3),
('Lisa', 'Wilson', 'lisa.wilson@company.com', '555-0108', '2019-12-01', 'Sales Manager', 85000.00, 4),
('James', 'Moore', 'james.moore@company.com', '555-0109', '2021-04-18', 'Financial Manager', 95000.00, 5),
('Patricia', 'Taylor', 'patricia.taylor@company.com', '555-0110', '2020-07-23', 'HR Specialist', 65000.00, 1);

-- Update department managers
UPDATE departments 
SET manager_id = 1 
WHERE department_name = 'Human Resources';

UPDATE departments 
SET manager_id = 2 
WHERE department_name = 'Engineering';

UPDATE departments 
SET manager_id = 3 
WHERE department_name = 'Marketing';

UPDATE departments 
SET manager_id = 4 
WHERE department_name = 'Sales';

UPDATE departments 
SET manager_id = 5 
WHERE department_name = 'Finance';

-- Update employee manager relationships
UPDATE employees 
SET manager_id = 1 
WHERE employee_id IN (10);

UPDATE employees 
SET manager_id = 2 
WHERE employee_id IN (6);

UPDATE employees 
SET manager_id = 3 
WHERE employee_id IN (8);

UPDATE employees 
SET manager_id = 4 
WHERE employee_id IN (7);

UPDATE employees 
SET manager_id = 5 
WHERE employee_id IN (9);

-- Insert sample projects
INSERT INTO projects (project_name, description, start_date, end_date, budget, status) VALUES
('Website Redesign', 'Complete overhaul of company website', '2023-01-15', '2023-06-30', 150000.00, 'Active'),
('Mobile App Development', 'Development of company mobile application', '2023-03-01', '2023-12-31', 300000.00, 'Active'),
('Marketing Campaign', 'Quarterly marketing campaign for new product', '2023-02-01', '2023-05-31', 100000.00, 'Active'),
('Financial Audit', 'Annual financial audit and reporting', '2023-01-01', '2023-03-31', 75000.00, 'Completed'),
('Employee Training Program', 'Comprehensive training program for new hires', '2023-04-01', '2023-09-30', 50000.00, 'Active');

-- Insert employee-project assignments
INSERT INTO employee_projects (employee_id, project_id, assigned_date, role, hours_worked) VALUES
(2, 1, '2023-01-15', 'Lead Developer', 80.00),
(6, 1, '2023-01-15', 'Developer', 60.00),
(3, 2, '2023-03-01', 'Product Manager', 40.00),
(2, 2, '2023-03-01', 'Lead Developer', 120.00),
(6, 2, '2023-03-01', 'Developer', 100.00),
(7, 3, '2023-02-01', 'Marketing Manager', 30.00),
(8, 3, '2023-02-01', 'Marketing Specialist', 20.00),
(9, 4, '2023-01-01', 'Financial Manager', 25.00),
(5, 4, '2023-01-01', 'Financial Analyst', 35.00),
(10, 5, '2023-04-01', 'HR Manager', 45.00),
(1, 5, '2023-04-01', 'HR Specialist', 30.00);