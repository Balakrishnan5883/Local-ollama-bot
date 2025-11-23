-- Transaction examples and logging mechanisms

-- Example of a transaction for updating employee salary and department
BEGIN TRANSACTION;

UPDATE employees 
SET salary = salary * 1.05, 
    updated_at = CURRENT_TIMESTAMP
WHERE employee_id = 1;

UPDATE departments 
SET updated_at = CURRENT_TIMESTAMP
WHERE department_id = (SELECT department_id FROM employees WHERE employee_id = 1);

-- If everything is successful, commit the transaction
COMMIT;

-- If there's an error, rollback the transaction
-- ROLLBACK;

-- Create a logging table for audit purposes
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation VARCHAR(10),
    record_id INT,
    old_values TEXT,
    new_values TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to log changes to employees table
CREATE OR REPLACE FUNCTION log_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_values, new_values, changed_by)
        VALUES ('employees', 'UPDATE', NEW.employee_id, 
                row_to_json(OLD)::TEXT, row_to_json(NEW)::TEXT, CURRENT_USER);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, record_id, new_values, changed_by)
        VALUES ('employees', 'INSERT', NEW.employee_id, 
                row_to_json(NEW)::TEXT, CURRENT_USER);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, record_id, old_values, changed_by)
        VALUES ('employees', 'DELETE', OLD.employee_id, 
                row_to_json(OLD)::TEXT, CURRENT_USER);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for employees table
CREATE TRIGGER employees_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION log_employee_changes();