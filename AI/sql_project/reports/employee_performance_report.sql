-- Employee Performance Report
-- This report analyzes employee performance based on project assignments and hours worked

-- 1. Overall employee performance ranking
WITH employee_performance AS (
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.job_title,
        d.department_name,
        COUNT(ep.project_id) AS projects_assigned,
        SUM(ep.hours_worked) AS total_hours_worked,
        AVG(ep.hours_worked) AS avg_hours_per_project,
        RANK() OVER (ORDER BY SUM(ep.hours_worked) DESC) AS performance_rank
    FROM employees e
    JOIN employee_projects ep ON e.employee_id = ep.employee_id
    JOIN departments d ON e.department_id = d.department_id
    GROUP BY e.employee_id, e.first_name, e.last_name, e.job_title, d.department_name
)
SELECT 
    employee_id,
    first_name,
    last_name,
    job_title,
    department_name,
    projects_assigned,
    total_hours_worked,
    ROUND(avg_hours_per_project, 2) AS avg_hours_per_project,
    performance_rank
FROM employee_performance
ORDER BY performance_rank;

-- 2. Department-wise performance comparison
SELECT 
    d.department_name,
    COUNT(DISTINCT e.employee_id) AS employee_count,
    COUNT(ep.project_id) AS total_projects,
    SUM(ep.hours_worked) AS total_hours_worked,
    AVG(ep.hours_worked) AS avg_hours_per_assignment,
    ROUND(SUM(ep.hours_worked) / NULLIF(COUNT(DISTINCT e.employee_id), 0), 2) AS avg_hours_per_employee
FROM departments d
JOIN employees e ON d.department_id = e.department_id
JOIN employee_projects ep ON e.employee_id = ep.employee_id
GROUP BY d.department_name
ORDER BY total_hours_worked DESC;

-- 3. High performing employees by department
WITH department_avg_hours AS (
    SELECT 
        d.department_name,
        AVG(ep.hours_worked) AS avg_hours_per_employee
    FROM departments d
    JOIN employees e ON d.department_id = e.department_id
    JOIN employee_projects ep ON e.employee_id = ep.employee_id
    GROUP BY d.department_name
),
employee_performance_with_avg AS (
    SELECT 
        e.employee_id,
        e.first_name,
        e.last_name,
        e.job_title,
        d.department_name,
        SUM(ep.hours_worked) AS total_hours_worked,
        da.avg_hours_per_employee,
        CASE 
            WHEN SUM(ep.hours_worked) > da.avg_hours_per_employee * 1.2 THEN 'High Performer'
            WHEN SUM(ep.hours_worked) > da.avg_hours_per_employee * 0.8 THEN 'Average Performer'
            ELSE 'Below Average'
        END AS performance_category
    FROM employees e
    JOIN employee_projects ep ON e.employee_id = ep.employee_id
    JOIN departments d ON e.department_id = d.department_id
    JOIN department_avg_hours da ON d.department_name = da.department_name
    GROUP BY e.employee_id, e.first_name, e.last_name, e.job_title, d.department_name, da.avg_hours_per_employee
)
SELECT 
    employee_id,
    first_name,
    last_name,
    job_title,
    department_name,
    total_hours_worked,
    ROUND(avg_hours_per_employee, 2) AS department_avg_hours,
    performance_category
FROM employee_performance_with_avg
ORDER BY department_name, total_hours_worked DESC;