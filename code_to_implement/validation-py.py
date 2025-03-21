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
        
        if entry_time >= exit_time:
            errors["exit_time"] = "Exit time must be after entry time"
    except (ValueError, TypeError) as e:
        if "entry_time" in str(e):
            errors["entry_time"] = "Invalid entry time format"
        else:
            errors["exit_time"] = "Invalid exit time format"
    
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
    payment_method = data.get("payment_method", "")
    if not payment_method:
        errors["payment_method"] = "Payment method is required"
    elif payment_method not in ["cash", "check"]:
        errors["payment_method"] = "Invalid payment method"
    
    # Check number required for check payments
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
    
    # Validate end date if provided
    if data.get("end_date"):
        try:
            end_date = parse_date(data.get("end_date"))
            start_date = parse_date(data.get("start_date"))
            
            if end_date < start_date:
                errors["end_date"] = "End date cannot be before start date"
        except (ValueError, TypeError):
            errors["end_date"] = "Invalid end date format"
    
    return errors

# Project cost validation
def validate_project_cost(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate project_id
    if not data.get("project_id"):
        errors["project_id"] = "Project is required"
    
    # Validate cost type
    cost_type = data.get("cost_type", "")
    if not cost_type:
        errors["cost_type"] = "Cost type is required"
    elif cost_type not in ["material", "employee"]:
        errors["cost_type"] = "Invalid cost type"
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Cost amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Cost amount must be a valid number"
    
    return errors

# Invoice validation
def validate_invoice(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate project_id
    if not data.get("project_id"):
        errors["project_id"] = "Project is required"
    
    # Validate amount charged
    try:
        amount_charged = float(data.get("amount_charged", 0))
        if amount_charged <= 0:
            errors["amount_charged"] = "Invoice amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount_charged"] = "Invoice amount must be a valid number"
    
    # Validate invoice date
    try:
        invoice_date = parse_date(data.get("invoice_date"))
    except (ValueError, TypeError):
        errors["invoice_date"] = "Invalid invoice date format"
    
    return errors

# Accounts payable validation
def validate_accounts_payable(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate supplier
    if not data.get("supplier"):
        errors["supplier"] = "Supplier is required"
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    
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
    except (ValueError, TypeError):
        errors["due_date"] = "Invalid due date format"
    
    # Validate payment method
    if not data.get("payment_method"):
        errors["payment_method"] = "Payment method is required"
    
    # Validate category
    if not data.get("category"):
        errors["category"] = "Category is required"
    
    # Validate status
    status = data.get("status", "")
    if not status:
        errors["status"] = "Status is required"
    elif status not in ["pending", "paid"]:
        errors["status"] = "Invalid status"
    
    return errors

# Paid account validation
def validate_paid_account(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate supplier
    if not data.get("supplier"):
        errors["supplier"] = "Supplier is required"
    
    # Validate amount paid
    try:
        amount_paid = float(data.get("amount_paid", 0))
        if amount_paid <= 0:
            errors["amount_paid"] = "Amount paid must be greater than zero"
    except (ValueError, TypeError):
        errors["amount_paid"] = "Amount paid must be a valid number"
    
    # Validate payment date
    try:
        payment_date = parse_date(data.get("payment_date"))
    except (ValueError, TypeError):
        errors["payment_date"] = "Invalid payment date format"
    
    # Validate payment method
    payment_method = data.get("payment_method", "")
    if not payment_method:
        errors["payment_method"] = "Payment method is required"
    
    # Check number required for check payments
    if payment_method == "check" and not data.get("check_number"):
        errors["check_number"] = "Check number is required for check payments"
    
    return errors

# Expense validation
def validate_expense(data: Dict[str, Any]) -> Dict[str, str]:
    errors = {}
    
    # Validate description
    if not data.get("description"):
        errors["description"] = "Description is required"
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount <= 0:
            errors["amount"] = "Amount must be greater than zero"
    except (ValueError, TypeError):
        errors["amount"] = "Amount must be a valid number"
    
    # Validate expense date
    try:
        expense_date = parse_date(data.get("expense_date"))
    except (ValueError, TypeError):
        errors["expense_date"] = "Invalid expense date format"
    
    # Validate category
    if not data.get("category"):
        errors["category"] = "Category is required"
    
    # Validate payment method
    if not data.get("payment_method"):
        errors["payment_method"] = "Payment method is required"
    
    return errors

# Helper functions
def parse_date(date_str: Optional[str]) -> date:
    """Parse date string to date object"""
    if not date_str:
        raise ValueError("Date is required")
    
    if isinstance(date_str, date):
        return date_str
    
    try:
        return parser.parse(date_str).date()
    except:
        raise ValueError(f"Invalid date format: {date_str}")

def parse_time(time_str: Optional[str]) -> time:
    """Parse time string to time object"""
    if not time_str:
        raise ValueError("Time is required")
    
    if isinstance(time_str, time):
        return time_str
    
    try:
        parsed_time = parser.parse(time_str).time()
        return parsed_time
    except:
        raise ValueError(f"Invalid time format: {time_str}")

# Function to validate form data and return validation errors
def validate_form_data(form_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate form data based on form type
    
    Args:
        form_type: Type of form to validate
        data: Form data dictionary
    
    Returns:
        Dictionary of field errors or empty dict if valid
    """
    if form_type == "employee":
        return validate_employee(data)
    elif form_type == "worklog":
        return validate_worklog(data)
    elif form_type == "payment":
        return validate_payment(data)
    elif form_type == "project":
        return validate_project(data)
    elif form_type == "project_cost":
        return validate_project_cost(data)
    elif form_type == "invoice":
        return validate_invoice(data)
    elif form_type == "accounts_payable":
        return validate_accounts_payable(data)
    elif form_type == "paid_account":
        return validate_paid_account(data)
    elif form_type == "expense":
        return validate_expense(data)
    else:
        return {}
