from datetime import datetime, date, time
from typing import Dict, Any, Optional, List, Union
from fastapi import HTTPException, status
from dateutil import parser

# Validation error class
class ValidationError(Exception):
    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        self.message = "Validation error"
        super().__init__(self.message)

# Employee validation
def validate_employee(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate name
    if not data.get("name"):
        errors["name"] = "Employee name is required"
    elif len(data.get("name", "")) > 100:
        errors["name"] = "Name is too long (maximum 100 characters)"
    
    # Validate hourly rate
    try:
        hourly_rate = float(data.get("hourly_rate", 0))
        if hourly_rate <= 0:
            errors["hourly_rate"] = "Hourly rate must be greater than zero"
    except (ValueError, TypeError):
        errors["hourly_rate"] = "Hourly rate must be a valid number"
    
    return errors

# Work log validation
def validate_worklog(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate employee_id
    if not data.get("employee_id"):
        errors["employee_id"] = "Employee is required"
    
    # Validate date
    try:
        log_date = parse_date(data.get("log_date"))
        if log_date > date.today():
            errors["log_date"] = "Work log date cannot be in the future"
    except (ValueError, TypeError):
        errors["log_date"] = "Invalid date format"
    
    # Validate entry and exit times
    try:
        entry_time = parse_time(data.get("entry_time"))
        exit_time = parse_time(data.get("exit_time"))
        
        if entry_time and exit_time and entry_time >= exit_time:
            errors["exit_time"] = "Exit time must be after entry time"
    except (ValueError, TypeError):
        if "entry_time" not in errors:
            errors["entry_time"] = "Invalid time format"
        if "exit_time" not in errors:
            errors["exit_time"] = "Invalid time format"
    
    # Validate lunch duration
    try:
        lunch_duration = int(data.get("lunch_duration", 0))
        if lunch_duration < 0:
            errors["lunch_duration"] = "Lunch duration cannot be negative"
    except (ValueError, TypeError):
        errors["lunch_duration"] = "Lunch duration must be a valid number"
    
    return errors

# Payment validation
def validate_payment(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate employee_id
    if not data.get("employee_id"):
        errors["employee_id"] = "Employee is required"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Payment amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Payment amount must be a valid number"
    
    # Validate payment method
    payment_method = data.get("payment_method", "").lower()
    if not payment_method:
        errors["payment_method"] = "Payment method is required"
    elif payment_method not in ["cash", "check", "direct deposit"]:
        errors["payment_method"] = "Invalid payment method"
    
    # Validate check number if payment method is check
    if payment_method == "check" and not data.get("check_number"):
        errors["check_number"] = "Check number is required for check payments"
    
    # Validate payment date
    try:
        payment_date = parse_date(data.get("payment_date"))
        if payment_date > date.today():
            errors["payment_date"] = "Payment date cannot be in the future"
    except (ValueError, TypeError):
        errors["payment_date"] = "Invalid date format"
    
    return errors

# Project validation
def validate_project(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate name
    if not data.get("name"):
        errors["name"] = "Project name is required"
    elif len(data.get("name", "")) > 100:
        errors["name"] = "Name is too long (maximum 100 characters)"
    
    # Validate client
    if not data.get("client"):
        errors["client"] = "Client name is required"
    elif len(data.get("client", "")) > 100:
        errors["client"] = "Client name is too long (maximum 100 characters)"
    
    # Validate value
    try:
        value = float(data.get("value", 0))
        if value <= 0:
            errors["value"] = "Project value must be greater than zero"
    except (ValueError, TypeError):
        errors["value"] = "Project value must be a valid number"
    
    # Validate start date
    try:
        start_date = parse_date(data.get("start_date"))
    except (ValueError, TypeError):
        errors["start_date"] = "Invalid start date format"
    
    # Validate end date
    try:
        end_date = parse_date(data.get("end_date"))
        start_date = parse_date(data.get("start_date"))
        
        if start_date and end_date and start_date > end_date:
            errors["end_date"] = "End date must be after start date"
    except (ValueError, TypeError):
        errors["end_date"] = "Invalid end date format"
    
    return errors

# Project cost validation
def validate_project_cost(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate project_id
    if not data.get("project_id"):
        errors["project_id"] = "Project is required"
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    elif len(data.get("description", "")) > 200:
        errors["description"] = "Description is too long (maximum 200 characters)"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Cost amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Cost amount must be a valid number"
    
    # Validate date
    try:
        cost_date = parse_date(data.get("date"))
        if cost_date > date.today():
            errors["date"] = "Cost date cannot be in the future"
    except (ValueError, TypeError):
        errors["date"] = "Invalid date format"
    
    return errors

# Invoice validation
def validate_invoice(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate project_id
    if not data.get("project_id"):
        errors["project_id"] = "Project is required"
    
    # Validate amount charged
    try:
        amount = float(data.get("amount_charged", 0))
        if amount <= 0:
            errors["amount_charged"] = "Invoice amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount_charged"] = "Invoice amount must be a valid number"
    
    # Validate invoice date
    try:
        invoice_date = parse_date(data.get("invoice_date"))
    except (ValueError, TypeError):
        errors["invoice_date"] = "Invalid date format"
    
    return errors

# Accounts payable validation
def validate_accounts_payable(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate vendor
    if not data.get("vendor"):
        errors["vendor"] = "Vendor name is required"
    elif len(data.get("vendor", "")) > 100:
        errors["vendor"] = "Vendor name is too long (maximum 100 characters)"
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    elif len(data.get("description", "")) > 200:
        errors["description"] = "Description is too long (maximum 200 characters)"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Amount must be a valid number"
    
    # Validate due date
    try:
        due_date = parse_date(data.get("due_date"))
        if due_date < date.today():
            errors["due_date"] = "Due date cannot be in the past"
    except (ValueError, TypeError):
        errors["due_date"] = "Invalid date format"
    
    # Validate invoice date
    try:
        invoice_date = parse_date(data.get("invoice_date"))
        due_date = parse_date(data.get("due_date"))
        
        if invoice_date and due_date and invoice_date > due_date:
            errors["invoice_date"] = "Invoice date cannot be after due date"
    except (ValueError, TypeError):
        errors["invoice_date"] = "Invalid date format"
    
    return errors

# Paid account validation
def validate_paid_account(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate accounts_payable_id
    if not data.get("accounts_payable_id"):
        errors["accounts_payable_id"] = "Account payable is required"
    
    # Validate payment method
    payment_method = data.get("payment_method", "").lower()
    if not payment_method:
        errors["payment_method"] = "Payment method is required"
    elif payment_method not in ["cash", "check", "direct deposit", "credit card"]:
        errors["payment_method"] = "Invalid payment method"
    
    # Validate check number if payment method is check
    if payment_method == "check" and not data.get("check_number"):
        errors["check_number"] = "Check number is required for check payments"
    
    # Validate payment date
    try:
        payment_date = parse_date(data.get("payment_date"))
        if payment_date > date.today():
            errors["payment_date"] = "Payment date cannot be in the future"
    except (ValueError, TypeError):
        errors["payment_date"] = "Invalid date format"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Payment amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Payment amount must be a valid number"
    
    return errors

# Expense validation
def validate_expense(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate category
    if not data.get("category"):
        errors["category"] = "Expense category is required"
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    elif len(data.get("description", "")) > 200:
        errors["description"] = "Description is too long (maximum 200 characters)"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Expense amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Expense amount must be a valid number"
    
    # Validate expense date
    try:
        expense_date = parse_date(data.get("expense_date"))
        if expense_date > date.today():
            errors["expense_date"] = "Expense date cannot be in the future"
    except (ValueError, TypeError):
        errors["expense_date"] = "Invalid date format"
    
    return errors

# Helper functions
def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None
    
    try:
        if isinstance(date_str, date):
            return date_str
        return parser.parse(date_str).date()
    except (ValueError, TypeError):
        raise ValueError(f"Invalid date format: {date_str}")

def parse_time(time_str: Optional[str]) -> Optional[time]:
    """Parse time string to time object"""
    if not time_str:
        return None
    
    try:
        if isinstance(time_str, time):
            return time_str
        return parser.parse(time_str).time()
    except (ValueError, TypeError):
        raise ValueError(f"Invalid time format: {time_str}")

def validate_form_data(form_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate form data based on form type
    
    Args:
        form_type: Type of form to validate
        data: Form data dictionary
    
    Returns:
        Dictionary of field errors or empty dict if valid
    """
    validation_functions = {
        "employee": validate_employee,
        "worklog": validate_worklog,
        "payment": validate_payment,
        "project": validate_project,
        "project_cost": validate_project_cost,
        "invoice": validate_invoice,
        "accounts_payable": validate_accounts_payable,
        "paid_account": validate_paid_account,
        "expense": validate_expense
    }
    
    if form_type not in validation_functions:
        return {"form": f"Unknown form type: {form_type}"}
    
    try:
        return validation_functions[form_type](data)
    except Exception as e:
        return {"database": f"Validation error: {str(e)}"}
