# Import the validation module
from validation import validate_form_data
from fastapi import HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import urlencode

# Update template to include validation errors and success messages
def render_template_with_errors(templates, template_name, request, errors=None, form_data=None, **kwargs):
    """Render template with validation errors and form data"""
    context = {
        "request": request, 
        "errors": errors or {}, 
        "form_data": form_data or {},
        **kwargs
    }
    return templates.TemplateResponse(template_name, context)

# Example of an updated route with validation (add_update_employee)
@app.post("/employees")
async def add_update_employee(
    request: Request,
    employee_id: Optional[int] = Form(None),
    name: str = Form(...),
    hourly_rate: float = Form(...),
    db: Session = Depends(get_db)
):
    """Add or update employee with validation"""
    # Create form data dictionary
    form_data = {
        "employee_id": employee_id,
        "name": name,
        "hourly_rate": hourly_rate
    }
    
    # Validate form data
    errors = validate_form_data("employee", form_data)
    
    # If there are validation errors, re-render the form with errors
    if errors:
        employees = db.query(models.Employee).all()
        return render_template_with_errors(
            templates, 
            "employees.html", 
            request, 
            errors=errors, 
            form_data=form_data,
            employees=employees,
            active_page="employees"
        )
    
    # Process valid form data
    try:
        if employee_id:
            # Update existing employee
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if employee:
                employee.name = name
                employee.hourly_rate = hourly_rate
        else:
            # Create new employee
            employee = models.Employee(name=name, hourly_rate=hourly_rate)
            db.add(employee)
        
        db.commit()
        
        # Redirect with success message
        success_message = "Employee successfully updated" if employee_id else "Employee successfully added"
        return RedirectResponse(url="/employees?" + urlencode({"success": success_message}), status_code=303)
    
    except Exception as e:
        # Handle database errors
        db.rollback()
        employees = db.query(models.Employee).all()
        return render_template_with_errors(
            templates, 
            "employees.html", 
            request, 
            errors={"database": f"Database error: {str(e)}"},
            form_data=form_data,
            employees=employees,
            active_page="employees"
        )

# Example of an updated route with validation (add_worklog)
@app.post("/worklogs")
async def add_worklog(
    request: Request,
    employee_id: int = Form(...),
    log_date: date = Form(...),
    entry_time: str = Form(...),
    exit_time: str = Form(...),
    lunch_duration: int = Form(...),
    db: Session = Depends(get_db)
):
    """Save work log with validation"""
    # Create form data dictionary
    form_data = {
        "employee_id": employee_id,
        "log_date": log_date,
        "entry_time": entry_time,
        "exit_time": exit_time,
        "lunch_duration": lunch_duration
    }
    
    # Validate form data
    errors = validate_form_data("worklog", form_data)
    
    # If there are validation errors, re-render the form with errors
    if errors:
        employees = db.query(models.Employee).all()
        worklogs = db.query(models.WorkLog).order_by(models.WorkLog.date.desc()).limit(20).all()
        return render_template_with_errors(
            templates, 
            "worklogs.html", 
            request, 
            errors=errors, 
            form_data=form_data,
            employees=employees,
            worklogs=worklogs,
            today=date.today(),
            active_page="worklogs"
        )
    
    # Process valid form data
    try:
        # Convert string times to time objects
        entry_time_obj = datetime.strptime(entry_time, "%H:%M").time()
        exit_time_obj = datetime.strptime(exit_time, "%H:%M").time()
        
        worklog = models.WorkLog(
            employee_id=employee_id,
            date=log_date,
            entry_time=entry_time_obj,
            exit_time=exit_time_obj,
            lunch_duration=lunch_duration
        )
        
        db.add(worklog)
        db.commit()
        
        # Redirect with success message
        return RedirectResponse(
            url="/worklogs?" + urlencode({"success": "Work log successfully added"}), 
            status_code=303
        )
    
    except Exception as e:
        # Handle database errors
        db.rollback()
        employees = db.query(models.Employee).all()
        worklogs = db.query(models.WorkLog).order_by(models.WorkLog.date.desc()).limit(20).all()
        return render_template_with_errors(
            templates, 
            "worklogs.html", 
            request, 
            errors={"database": f"Database error: {str(e)}"},
            form_data=form_data,
            employees=employees,
            worklogs=worklogs,
            today=date.today(),
            active_page="worklogs"
        )

# Example of a delete route with confirmation
@app.post("/employees/delete/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Delete an employee with proper error handling"""
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not employee:
            # Employee not found
            return RedirectResponse(
                url="/employees?" + urlencode({"error": "Employee not found"}), 
                status_code=303
            )
        
        # Check if employee has related records
        has_worklogs = db.query(models.WorkLog).filter(models.WorkLog.employee_id == employee_id).first() is not None
        has_payments = db.query(models.Payment).filter(models.Payment.employee_id == employee_id).first() is not None
        
        if has_worklogs or has_payments:
            # Cannot delete employee with related records
            return RedirectResponse(
                url="/employees?" + urlencode({
                    "error": "Cannot delete employee with related work logs or payments"
                }), 
                status_code=303
            )
        
        # Delete employee
        db.delete(employee)
        db.commit()
        
        # Redirect with success message
        return RedirectResponse(
            url="/employees?" + urlencode({"success": "Employee successfully deleted"}), 
            status_code=303
        )
    
    except Exception as e:
        # Handle database errors
        db.rollback()
        return RedirectResponse(
            url="/employees?" + urlencode({"error": f"Error deleting employee: {str(e)}"}), 
            status_code=303
        )

# Example of an updated route with validation (process_payment)
@app.post("/payroll")
async def process_payment(
    request: Request,
    employee_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    payment_date: date = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Record payment with validation"""
    # Create form data dictionary
    form_data = {
        "employee_id": employee_id,
        "amount": amount,
        "payment_method": payment_method,
        "payment_date": payment_date,
        "notes": notes
    }
    
    # Add check fields if payment method is check
    if payment_method == "check":
        form_data["check_number"] = request.form.get("check_number", "")
        form_data["check_bank"] = request.form.get("check_bank", "")
    
    # Validate form data
    errors = validate_form_data("payment", form_data)
    
    # If there are validation errors, re-render the form with errors
    if errors:
        # Get all the data needed for the payroll page
        selected_date = payment_date or date.today()
        start_date, end_date = get_week_dates(selected_date)
        employees = db.query(models.Employee).all()
        payroll_data = []
        for employee in employees:
            worklogs = db.query(models.WorkLog).filter(
                models.WorkLog.employee_id == employee.id,
                models.WorkLog.date >= start_date,
                models.WorkLog.date <= end_date
            ).all()
            
            total_hours = sum(worklog.hours_worked for worklog in worklogs)
            amount_due = total_hours * employee.hourly_rate
            
            payroll_data.append({
                "employee": employee,
                "worklogs": worklogs,
                "total_hours": total_hours,
                "amount_due": amount_due
            })
        recent_payments = db.query(models.Payment).order_by(models.Payment.payment_date.desc()).limit(10).all()
        
        return render_template_with_errors(
            templates, 
            "payroll.html", 
            request, 
            errors=errors, 
            form_data=form_data,
            payroll_data=payroll_data,
            start_date=start_date,
            end_date=end_date,
            selected_date=selected_date,
            recent_payments=recent_payments,
            active_page="payroll"
        )
    
    # Process valid form data
    try:
        payment = models.Payment(
            employee_id=employee_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            notes=notes
        )
        
        # Add check details if payment method is check
        if payment_method == "check":
            payment.check_number = form_data.get("check_number")
            payment.check_bank = form_data.get("check_bank")
        
        db.add(payment)
        db.commit()
        
        # Redirect with success message
        return RedirectResponse(
            url="/payroll?" + urlencode({"success": "Payment successfully processed"}), 
            status_code=303
        )
    
    except Exception as e:
        # Handle database errors
        db.rollback()
        return RedirectResponse(
            url="/payroll?" + urlencode({"error": f"Error processing payment: {str(e)}"}), 
            status_code=303
        )

# Add these implementations to your existing app.py file
# Implement similar validation for all other form submissions
