-- Additional constraints and validation rules for production use

-- Add check constraints for data validation
ALTER TABLE employees 
ADD CONSTRAINT chk_salary_positive 
CHECK (salary > 0);

ALTER TABLE employees 
ADD CONSTRAINT chk_hire_date 
CHECK (hire_date <= CURRENT_DATE);

ALTER TABLE projects 
ADD CONSTRAINT chk_project_dates 
CHECK (start_date <= end_date OR end_date IS NULL);

ALTER TABLE projects 
ADD CONSTRAINT chk_budget_positive 
CHECK (budget >= 0);

ALTER TABLE employee_projects 
ADD CONSTRAINT chk_hours_positive 
CHECK (hours_worked >= 0);

-- Add unique constraint on email (already exists in table creation but added here for emphasis)
ALTER TABLE employees 
ADD CONSTRAINT uk_email 
UNIQUE (email);

-- Add check constraint for status values in projects
ALTER TABLE projects 
ADD CONSTRAINT chk_project_status 
CHECK (status IN ('Active', 'Completed', 'On Hold', 'Cancelled'));

-- Add check constraint for job titles (optional but good for data quality)
ALTER TABLE employees 
ADD CONSTRAINT chk_job_title 
CHECK (job_title IS NOT NULL AND job_title <> '');

-- Add check constraint for phone numbers (basic validation)
ALTER TABLE employees 
ADD CONSTRAINT chk_phone 
CHECK (phone IS NULL OR phone ~ '^[0-9\-\(\)\s]+$');

-- Add a constraint to prevent employees from being their own manager
ALTER TABLE employees 
ADD CONSTRAINT chk_manager_not_self 
CHECK (employee_id <> manager_id OR manager_id IS NULL);

-- Add a constraint to ensure department managers are employees of that department
ALTER TABLE departments 
ADD CONSTRAINT chk_manager_in_department 
CHECK (manager_id IS NULL OR manager_id IN (SELECT employee_id FROM employees WHERE department_id = departments.department_id));

-- Add a constraint to prevent duplicate assignments
-- This is already handled by the primary key in employee_projects, but can be reinforced
ALTER TABLE employee_projects 
ADD CONSTRAINT chk_unique_assignment 
UNIQUE (employee_id, project_id);