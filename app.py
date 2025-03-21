from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
import urllib.parse

from construction_erp import models
from construction_erp.database import engine, get_db
from construction_erp.validation import validate_form_data, ValidationError

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction ERP")

# Set up templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Helper functions
def get_week_dates(selected_date=None):
    """Get start and end dates for the week containing the selected date"""
    if not selected_date:
        selected_date = date.today()
    
    # Find the Monday of the week
    start_date = selected_date - timedelta(days=selected_date.weekday())
    # Find the Sunday of the week
    end_date = start_date + timedelta(days=6)
    
    return start_date, end_date

# Routes
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """Dashboard with summary data"""
    # Get current month data
    today = date.today()
    start_date = date(today.year, today.month, 1)
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    # Payroll total for current month
    payments = db.query(models.Payment).filter(
        models.Payment.payment_date >= start_date,
        models.Payment.payment_date <= end_date
    ).all()
    payroll_total = sum(payment.amount for payment in payments)
    
    # Invoice total for current month
    invoices = db.query(models.Invoice).filter(
        models.Invoice.invoice_date >= start_date,
        models.Invoice.invoice_date <= end_date
    ).all()
    invoice_total = sum(invoice.amount_charged for invoice in invoices)
    
    # Expense total for current month
    expenses = db.query(models.Expense).filter(
        models.Expense.expense_date >= start_date,
        models.Expense.expense_date <= end_date
    ).all()
    expense_total = sum(expense.amount for expense in expenses)
    
    # Upcoming payments (due in the next 30 days)
    upcoming_date = today + timedelta(days=30)
    upcoming_payables = db.query(models.AccountsPayable).filter(
        models.AccountsPayable.due_date >= today,
        models.AccountsPayable.due_date <= upcoming_date,
        models.AccountsPayable.status == "pending"
    ).order_by(models.AccountsPayable.due_date).limit(5).all()
    
    # Active projects (those with no end date or end date in the future)
    active_projects = db.query(models.Project).filter(
        (models.Project.end_date == None) | (models.Project.end_date >= today)
    ).order_by(models.Project.start_date.desc()).limit(5).all()
    
    # Recent activity (combine payments, invoices, expenses, paid accounts)
    recent_activity = []
    
    # Add payments
    for payment in db.query(models.Payment).order_by(models.Payment.payment_date.desc()).limit(5).all():
        recent_activity.append({
            "type": "payment",
            "date": payment.payment_date,
            "description": f"Payment to {payment.employee.name}",
            "amount": payment.amount
        })
    
    # Add invoices
    for invoice in db.query(models.Invoice).order_by(models.Invoice.invoice_date.desc()).limit(5).all():
        recent_activity.append({
            "type": "invoice",
            "date": invoice.invoice_date,
            "description": f"Invoice for {invoice.project.name}",
            "amount": invoice.amount_charged
        })
    
    # Add expenses
    for expense in db.query(models.Expense).order_by(models.Expense.expense_date.desc()).limit(5).all():
        recent_activity.append({
            "type": "expense",
            "date": expense.expense_date,
            "description": expense.description,
            "amount": expense.amount
        })
    
    # Add paid accounts
    for account in db.query(models.PaidAccount).order_by(models.PaidAccount.payment_date.desc()).limit(5).all():
        recent_activity.append({
            "type": "paid_account",
            "date": account.payment_date,
            "description": f"Payment to {account.supplier}",
            "amount": account.amount_paid
        })
    
    # Sort by date (newest first)
    recent_activity.sort(key=lambda x: x["date"], reverse=True)
    recent_activity = recent_activity[:10]  # Limit to 10 items
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "active_page": "home",
            "payroll_total": payroll_total,
            "invoice_total": invoice_total,
            "expense_total": expense_total,
            "upcoming_payables": upcoming_payables,
            "active_projects": active_projects,
            "recent_activity": recent_activity
        }
    )

# Employee Management
@app.get("/employees")
async def employees_page(request: Request, db: Session = Depends(get_db)):
    """Display list of employees with add/edit forms"""
    employees = db.query(models.Employee).all()
    return templates.TemplateResponse(
        "employees.html", 
        {"request": request, "employees": employees, "active_page": "employees", "errors": {}, "form_data": {}}
    )

@app.post("/employees")
async def add_update_employee(
    request: Request,
    employee_id: Optional[int] = Form(None),
    name: str = Form(...),
    hourly_rate: float = Form(...),
    db: Session = Depends(get_db)
):
    """Add or update employee"""
    # Prepare form data for validation and potential re-display
    form_data = {"name": name, "hourly_rate": hourly_rate}
    if employee_id:
        form_data["employee_id"] = employee_id
    
    # Validate form data
    errors = validate_form_data("employee", form_data)
    
    if errors:
        # If validation fails, re-render the form with errors
        employees = db.query(models.Employee).all()
        return templates.TemplateResponse(
            "employees.html",
            {"request": request, "employees": employees, "active_page": "employees", 
             "errors": errors, "form_data": form_data},
            status_code=422
        )
    
    try:
        if employee_id:
            # Update existing employee
            employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
            if employee:
                employee.name = name
                employee.hourly_rate = hourly_rate
                success_message = f"Employee {name} updated successfully"
            else:
                raise HTTPException(status_code=404, detail="Employee not found")
        else:
            # Create new employee
            employee = models.Employee(name=name, hourly_rate=hourly_rate)
            db.add(employee)
            success_message = f"Employee {name} added successfully"
        
        db.commit()
        # Redirect with success message
        return RedirectResponse(
            url=f"/employees?success={urllib.parse.quote(success_message)}", 
            status_code=303
        )
    except Exception as e:
        db.rollback()
        # Redirect with error message
        error_message = f"Error saving employee: {str(e)}"
        return RedirectResponse(
            url=f"/employees?error={urllib.parse.quote(error_message)}", 
            status_code=303
        )

@app.post("/employees/delete/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Delete an employee"""
    try:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Check if employee has related records (work logs, payments)
        work_logs = db.query(models.WorkLog).filter(models.WorkLog.employee_id == employee_id).count()
        payments = db.query(models.Payment).filter(models.Payment.employee_id == employee_id).count()
        
        if work_logs > 0 or payments > 0:
            warning = f"Employee has {work_logs} work logs and {payments} payment records. These will also be deleted."
        
        # Get employee name for success message
        employee_name = employee.name
        
        db.delete(employee)
        db.commit()
        
        # Redirect with success message
        success_message = f"Employee {employee_name} deleted successfully"
        return RedirectResponse(
            url=f"/employees?success={urllib.parse.quote(success_message)}", 
            status_code=303
        )
    except Exception as e:
        db.rollback()
        # Redirect with error message
        error_message = f"Error deleting employee: {str(e)}"
        return RedirectResponse(
            url=f"/employees?error={urllib.parse.quote(error_message)}", 
            status_code=303
        )

# Work Log Entry
@app.get("/worklogs")
async def worklogs_page(request: Request, db: Session = Depends(get_db)):
    """Form for entering work logs"""
    employees = db.query(models.Employee).all()
    worklogs = db.query(models.WorkLog).order_by(models.WorkLog.date.desc()).limit(20).all()
    
    return templates.TemplateResponse(
        "worklogs.html", 
        {
            "request": request, 
            "employees": employees, 
            "worklogs": worklogs,
            "today": date.today(),
            "active_page": "worklogs"
        }
    )

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
    """Save work log"""
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
    
    return RedirectResponse(url="/worklogs", status_code=303)

@app.post("/worklogs/delete/{worklog_id}")
async def delete_worklog(worklog_id: int, db: Session = Depends(get_db)):
    """Delete a work log"""
    worklog = db.query(models.WorkLog).filter(models.WorkLog.id == worklog_id).first()
    if not worklog:
        raise HTTPException(status_code=404, detail="Work log not found")
    
    db.delete(worklog)
    db.commit()
    
    return RedirectResponse(url="/worklogs", status_code=303)

# Payroll Processing
@app.get("/payroll")
async def payroll_page(
    request: Request, 
    week_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Display work logs for a week and calculate payroll"""
    if week_date:
        selected_date = datetime.strptime(week_date, "%Y-%m-%d").date()
    else:
        selected_date = date.today()
    
    start_date, end_date = get_week_dates(selected_date)
    
    # Get all employees
    employees = db.query(models.Employee).all()
    
    # Calculate payroll for each employee for the selected week
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
    
    # Get recent payments
    recent_payments = db.query(models.Payment).order_by(models.Payment.payment_date.desc()).limit(10).all()
    
    return templates.TemplateResponse(
        "payroll.html", 
        {
            "request": request, 
            "payroll_data": payroll_data,
            "start_date": start_date,
            "end_date": end_date,
            "selected_date": selected_date,
            "recent_payments": recent_payments,
            "active_page": "payroll"
        }
    )

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
    """Record payment"""
    payment = models.Payment(
        employee_id=employee_id,
        amount=amount,
        payment_method=payment_method,
        payment_date=payment_date,
        notes=notes
    )
    
    db.add(payment)
    db.commit()
    
    return RedirectResponse(url="/payroll", status_code=303)

# Project Management
@app.get("/projects")
async def projects_page(request: Request, db: Session = Depends(get_db)):
    """List projects with add/edit forms and cost entry"""
    projects = db.query(models.Project).all()
    return templates.TemplateResponse(
        "projects.html", 
        {"request": request, "projects": projects, "active_page": "projects"}
    )

@app.post("/projects")
async def add_update_project(
    request: Request,
    project_id: Optional[int] = Form(None),
    name: str = Form(...),
    value: float = Form(...),
    start_date: date = Form(...),
    end_date: Optional[date] = Form(None),
    db: Session = Depends(get_db)
):
    """Add or update project"""
    if project_id:
        # Update existing project
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if project:
            project.name = name
            project.value = value
            project.start_date = start_date
            project.end_date = end_date
    else:
        # Create new project
        project = models.Project(
            name=name, 
            value=value, 
            start_date=start_date, 
            end_date=end_date
        )
        db.add(project)
    
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)

@app.post("/projects/delete/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)

@app.post("/project_costs")
async def add_project_cost(
    request: Request,
    project_id: int = Form(...),
    cost_type: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_db)
):
    """Add project cost"""
    cost = models.ProjectCost(
        project_id=project_id,
        cost_type=cost_type,
        description=description,
        amount=amount
    )
    
    db.add(cost)
    db.commit()
    
    return RedirectResponse(url="/projects", status_code=303)

@app.post("/project_costs/delete/{cost_id}")
async def delete_project_cost(cost_id: int, db: Session = Depends(get_db)):
    """Delete a project cost"""
    cost = db.query(models.ProjectCost).filter(models.ProjectCost.id == cost_id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Project cost not found")
    
    db.delete(cost)
    db.commit()
    
    return RedirectResponse(url="/projects", status_code=303)

# Invoicing
@app.get("/invoices")
async def invoices_page(request: Request, db: Session = Depends(get_db)):
    """Form to select project and enter invoice details"""
    projects = db.query(models.Project).all()
    invoices = db.query(models.Invoice).order_by(models.Invoice.invoice_date.desc()).all()
    
    return templates.TemplateResponse(
        "invoices.html", 
        {
            "request": request, 
            "projects": projects, 
            "invoices": invoices,
            "active_page": "invoices"
        }
    )

@app.post("/invoices")
async def add_invoice(
    request: Request,
    project_id: int = Form(...),
    amount_charged: float = Form(...),
    invoice_date: date = Form(...),
    db: Session = Depends(get_db)
):
    """Save invoice"""
    invoice = models.Invoice(
        project_id=project_id,
        amount_charged=amount_charged,
        invoice_date=invoice_date
    )
    
    db.add(invoice)
    db.commit()
    
    return RedirectResponse(url="/invoices", status_code=303)

@app.post("/invoices/delete/{invoice_id}")
async def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Delete an invoice"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    db.delete(invoice)
    db.commit()
    
    return RedirectResponse(url="/invoices", status_code=303)

# Financial Management
@app.get("/financials")
async def financials_page(request: Request, db: Session = Depends(get_db)):
    """Tabs or sections for Accounts Payable, Paid Accounts, Expenses"""
    payables = db.query(models.AccountsPayable).all()
    paid_accounts = db.query(models.PaidAccount).all()
    expenses = db.query(models.Expense).all()
    
    return templates.TemplateResponse(
        "financials.html", 
        {
            "request": request, 
            "payables": payables, 
            "paid_accounts": paid_accounts,
            "expenses": expenses,
            "active_page": "financials"
        }
    )

@app.post("/financials/payables")
async def add_payable(
    request: Request,
    supplier: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    due_date: date = Form(...),
    payment_method: str = Form(...),
    category: str = Form(...),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add accounts payable"""
    payable = models.AccountsPayable(
        supplier=supplier,
        description=description,
        amount=amount,
        due_date=due_date,
        payment_method=payment_method,
        category=category,
        status=status,
        notes=notes
    )
    
    db.add(payable)
    db.commit()
    
    return RedirectResponse(url="/financials", status_code=303)

@app.post("/financials/paid")
async def add_paid_account(
    request: Request,
    supplier: str = Form(...),
    amount_paid: float = Form(...),
    payment_date: date = Form(...),
    payment_method: str = Form(...),
    check_number: Optional[str] = Form(None),
    check_bank: Optional[str] = Form(None),
    payment_proof: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add paid account"""
    paid_account = models.PaidAccount(
        supplier=supplier,
        amount_paid=amount_paid,
        payment_date=payment_date,
        payment_method=payment_method,
        check_number=check_number,
        check_bank=check_bank,
        payment_proof=payment_proof,
        notes=notes
    )
    
    db.add(paid_account)
    db.commit()
    
    return RedirectResponse(url="/financials", status_code=303)

@app.post("/financials/expenses")
async def add_expense(
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    expense_date: date = Form(...),
    category: str = Form(...),
    payment_method: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add expense"""
    expense = models.Expense(
        description=description,
        amount=amount,
        expense_date=expense_date,
        category=category,
        payment_method=payment_method,
        notes=notes
    )
    
    db.add(expense)
    db.commit()
    
    return RedirectResponse(url="/financials", status_code=303)

@app.post("/financials/delete/{type}/{item_id}")
async def delete_financial_item(type: str, item_id: int, db: Session = Depends(get_db)):
    """Delete specific financial entry"""
    if type == "payable":
        item = db.query(models.AccountsPayable).filter(models.AccountsPayable.id == item_id).first()
    elif type == "paid":
        item = db.query(models.PaidAccount).filter(models.PaidAccount.id == item_id).first()
    elif type == "expense":
        item = db.query(models.Expense).filter(models.Expense.id == item_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    
    return RedirectResponse(url="/financials", status_code=303)

# Reports
@app.get("/reports")
async def reports_page(
    request: Request, 
    report_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Navigation to all reports with date range filters"""
    # Default to current month if no dates provided
    if not start_date:
        today = date.today()
        start_date = date(today.year, today.month, 1).isoformat()
    
    if not end_date:
        today = date.today()
        # Last day of current month
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)
        end_date = end_date.isoformat()
    
    # Convert string dates to date objects
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    report_data = None
    
    if report_type == "payroll":
        # Payroll Report
        payments = db.query(models.Payment).filter(
            models.Payment.payment_date >= start_date_obj,
            models.Payment.payment_date <= end_date_obj
        ).order_by(models.Payment.payment_date).all()
        
        report_data = {
            "payments": payments,
            "total": sum(payment.amount for payment in payments)
        }
    
    elif report_type == "payment_method":
        # Payment Method Report
        payments = db.query(models.Payment).filter(
            models.Payment.payment_date >= start_date_obj,
            models.Payment.payment_date <= end_date_obj
        ).all()
        
        cash_total = sum(payment.amount for payment in payments if payment.payment_method == "cash")
        check_total = sum(payment.amount for payment in payments if payment.payment_method == "check")
        
        report_data = {
            "cash_total": cash_total,
            "check_total": check_total,
            "total": cash_total + check_total
        }
    
    elif report_type == "hours_worked":
        # Hours Worked Report
        employees = db.query(models.Employee).all()
        hours_data = []
        
        for employee in employees:
            worklogs = db.query(models.WorkLog).filter(
                models.WorkLog.employee_id == employee.id,
                models.WorkLog.date >= start_date_obj,
                models.WorkLog.date <= end_date_obj
            ).all()
            
            total_hours = sum(worklog.hours_worked for worklog in worklogs)
            
            hours_data.append({
                "employee": employee,
                "total_hours": total_hours
            })
        
        report_data = {"hours_data": hours_data}
    
    elif report_type == "project_billing":
        # Project Billing Report
        projects = db.query(models.Project).all()
        billing_data = []
        
        for project in projects:
            invoices = db.query(models.Invoice).filter(
                models.Invoice.project_id == project.id,
                models.Invoice.invoice_date >= start_date_obj,
                models.Invoice.invoice_date <= end_date_obj
            ).all()
            
            total_invoiced = sum(invoice.amount_charged for invoice in invoices)
            
            billing_data.append({
                "project": project,
                "total_invoiced": total_invoiced,
                "total_costs": project.total_costs,
                "profit": total_invoiced - project.total_costs
            })
        
        report_data = {"billing_data": billing_data}
    
    elif report_type == "project_cost":
        # Project Cost Report
        projects = db.query(models.Project).all()
        cost_data = []
        
        for project in projects:
            material_costs = sum(cost.amount for cost in project.costs if cost.cost_type == "material")
            employee_costs = sum(cost.amount for cost in project.costs if cost.cost_type == "employee")
            
            cost_data.append({
                "project": project,
                "material_costs": material_costs,
                "employee_costs": employee_costs,
                "total_costs": material_costs + employee_costs
            })
        
        report_data = {"cost_data": cost_data}
    
    elif report_type == "project_profit":
        # Project Profit Margin Report
        projects = db.query(models.Project).all()
        profit_data = []
        
        for project in projects:
            invoices = db.query(models.Invoice).filter(models.Invoice.project_id == project.id).all()
            total_invoiced = sum(invoice.amount_charged for invoice in invoices)
            
            profit_data.append({
                "project": project,
                "total_invoiced": total_invoiced,
                "total_costs": project.total_costs,
                "profit_margin": total_invoiced - project.total_costs,
                "profit_percentage": (total_invoiced - project.total_costs) / total_invoiced * 100 if total_invoiced > 0 else 0
            })
        
        report_data = {"profit_data": profit_data}
    
    elif report_type == "accounts_payable":
        # Accounts Payable Report
        payables = db.query(models.AccountsPayable).filter(
            models.AccountsPayable.due_date >= start_date_obj,
            models.AccountsPayable.due_date <= end_date_obj,
            models.AccountsPayable.status == "pending"
        ).order_by(models.AccountsPayable.due_date).all()
        
        report_data = {
            "payables": payables,
            "total": sum(payable.amount for payable in payables)
        }
    
    elif report_type == "paid_accounts":
        # Paid Accounts Report
        paid_accounts = db.query(models.PaidAccount).filter(
            models.PaidAccount.payment_date >= start_date_obj,
            models.PaidAccount.payment_date <= end_date_obj
        ).order_by(models.PaidAccount.payment_date).all()
        
        report_data = {
            "paid_accounts": paid_accounts,
            "total": sum(account.amount_paid for account in paid_accounts)
        }
    
    elif report_type == "monthly_expense":
        # Monthly Expense Report
        expenses = db.query(models.Expense).filter(
            models.Expense.expense_date >= start_date_obj,
            models.Expense.expense_date <= end_date_obj
        ).order_by(models.Expense.expense_date).all()
        
        # Group by category
        categories = {}
        for expense in expenses:
            if expense.category not in categories:
                categories[expense.category] = 0
            categories[expense.category] += expense.amount
        
        report_data = {
            "expenses": expenses,
            "categories": categories,
            "total": sum(expense.amount for expense in expenses)
        }
    
    elif report_type == "paid_by_method":
        # Paid Accounts by Payment Method
        paid_accounts = db.query(models.PaidAccount).filter(
            models.PaidAccount.payment_date >= start_date_obj,
            models.PaidAccount.payment_date <= end_date_obj
        ).all()
        
        methods = {}
        for account in paid_accounts:
            if account.payment_method not in methods:
                methods[account.payment_method] = 0
            methods[account.payment_method] += account.amount_paid
        
        report_data = {
            "methods": methods,
            "total": sum(account.amount_paid for account in paid_accounts)
        }
    
    elif report_type == "payment_forecast":
        # Payment Forecast
        payables = db.query(models.AccountsPayable).filter(
            models.AccountsPayable.status == "pending"
        ).order_by(models.AccountsPayable.due_date).all()
        
        # Group by month
        forecast = {}
        for payable in payables:
            month_key = f"{payable.due_date.year}-{payable.due_date.month:02d}"
            if month_key not in forecast:
                forecast[month_key] = 0
            forecast[month_key] += payable.amount
        
        report_data = {
            "payables": payables,
            "forecast": forecast,
            "total": sum(payable.amount for payable in payables)
        }
    
    return templates.TemplateResponse(
        "reports.html", 
        {
            "request": request, 
            "report_type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "report_data": report_data,
            "active_page": "reports"
        }
    )

# Documentation
@app.get("/documentation")
async def documentation_page(request: Request):
    """Display system documentation"""
    return templates.TemplateResponse(
        "documentation.html", 
        {"request": request, "active_page": "documentation"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
