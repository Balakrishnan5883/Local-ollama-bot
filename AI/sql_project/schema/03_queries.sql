-- Basic SELECT queries
-- 1. Get all employees
SELECT * FROM employees;

-- 2. Get employees with their department names
SELECT e.first_name, e.last_name, e.job_title, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 3. Get employees with their manager names
SELECT 
    e.first_name AS employee_first_name,
    e.last_name AS employee_last_name,
    m.first_name AS manager_first_name,
    m.last_name AS manager_last_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id;

-- JOINs (INNER, LEFT, RIGHT, FULL)
-- 4. INNER JOIN: Employees and their projects
SELECT e.first_name, e.last_name, p.project_name, ep.role
FROM employees e
INNER JOIN employee_projects ep ON e.employee_id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.project_id;

-- 5. LEFT JOIN: All employees and their projects (including those without projects)
SELECT e.first_name, e.last_name, p.project_name, ep.role
FROM employees e
LEFT JOIN employee_projects ep ON e.employee_id = ep.employee_id
LEFT JOIN projects p ON ep.project_id = p.project_id;

-- 6. RIGHT JOIN: All projects and their assigned employees
SELECT e.first_name, e.last_name, p.project_name, ep.role
FROM employees e
RIGHT JOIN employee_projects ep ON e.employee_id = ep.employee_id
RIGHT JOIN projects p ON ep.project_id = p.project_id;

-- Aggregation with GROUP BY
-- 7. Average salary by department
SELECT d.department_name, AVG(e.salary) AS average_salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
GROUP BY d.department_name;

-- 8. Total hours worked by employee
SELECT e.first_name, e.last_name, SUM(ep.hours_worked) AS total_hours
FROM employees e
JOIN employee_projects ep ON e.employee_id = ep.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name;

-- 9. Project budget vs hours worked
SELECT 
    p.project_name,
    p.budget,
    SUM(ep.hours_worked) AS total_hours_worked,
    (p.budget / NULLIF(SUM(ep.hours_worked), 0)) AS budget_per_hour
FROM projects p
JOIN employee_projects ep ON p.project_id = ep.project_id
GROUP BY p.project_id, p.project_name, p.budget;

-- Subqueries
-- 10. Employees earning above average salary
SELECT first_name, last_name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 11. Projects with more than 2 employees assigned
SELECT p.project_name, COUNT(ep.employee_id) AS employee_count
FROM projects p
JOIN employee_projects ep ON p.project_id = ep.project_id
GROUP BY p.project_id, p.project_name
HAVING COUNT(ep.employee_id) > 2;

-- Window Functions
-- 12. Salary ranking within departments
SELECT 
    e.first_name,
    e.last_name,
    e.salary,
    d.department_name,
    ROW_NUMBER() OVER (PARTITION BY d.department_name ORDER BY e.salary DESC) AS salary_rank
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 13. Cumulative salary by hire date
SELECT 
    first_name,
    last_name,
    hire_date,
    salary,
    SUM(salary) OVER (ORDER BY hire_date) AS cumulative_salary
FROM employees;

-- CTEs (Common Table Expressions)
-- 14. CTE to find employees in high-budget departments
WITH high_budget_departments AS (
    SELECT department_id, department_name, budget
    FROM departments
    WHERE budget > 1000000
),
employee_in_high_budget AS (
    SELECT e.employee_id, e.first_name, e.last_name, e.salary, d.department_name
    FROM employees e
    JOIN high_budget_departments d ON e.department_id = d.department_id
)
SELECT * FROM employee_in_high_budget;

-- 15. CTE to calculate project efficiency
WITH project_hours AS (
    SELECT 
        p.project_id,
        p.project_name,
        SUM(ep.hours_worked) AS total_hours,
        p.budget
    FROM projects p
    JOIN employee_projects ep ON p.project_id = ep.project_id
    GROUP BY p.project_id, p.project_name, p.budget
)
SELECT 
    project_name,
    total_hours,
    budget,
    (budget / NULLIF(total_hours, 0)) AS efficiency_ratio
FROM project_hours
ORDER BY efficiency_ratio DESC;

-- Advanced Queries
-- 16. Employees with their department budget and salary ratio
SELECT 
    e.first_name,
    e.last_name,
    d.department_name,
    d.budget AS department_budget,
    e.salary,
    (e.salary / NULLIF(d.budget, 0)) * 100 AS salary_percentage_of_budget
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 17. Department-wise performance metrics
SELECT 
    d.department_name,
    COUNT(e.employee_id) AS employee_count,
    AVG(e.salary) AS average_salary,
    SUM(e.salary) AS total_salary,
    MAX(e.salary) AS max_salary,
    MIN(e.salary) AS min_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name;

-- 18. Project status analysis
SELECT 
    status,
    COUNT(*) AS project_count,
    AVG(budget) AS average_budget,
    SUM(budget) AS total_budget
FROM projects
GROUP BY status;

-- 19. Top 3 employees by hours worked
SELECT 
    e.first_name,
    e.last_name,
    SUM(ep.hours_worked) AS total_hours
FROM employees e
JOIN employee_projects ep ON e.employee_id = ep.employee_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY total_hours DESC
LIMIT 3;

-- 20. Employees with their full details using view
SELECT * FROM employee_details;

-- 21. Project assignments using view
SELECT * FROM project_assignments;

-- 22. Using function to calculate project hours
SELECT 
    project_name,
    calculate_project_hours(project_id) AS total_hours
FROM projects;