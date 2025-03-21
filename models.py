from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, Time, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date, time

from construction_erp.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    hourly_rate = Column(Float)
    
    # Relationships
    worklogs = relationship("WorkLog", back_populates="employee")
    payments = relationship("Payment", back_populates="employee")


class WorkLog(Base):
    __tablename__ = "worklogs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    entry_time = Column(Time)
    exit_time = Column(Time)
    lunch_duration = Column(Integer)  # in minutes
    
    # Relationships
    employee = relationship("Employee", back_populates="worklogs")
    
    @property
    def hours_worked(self):
        """Calculate hours worked with lunch deduction"""
        entry_datetime = datetime.combine(date.today(), self.entry_time)
        exit_datetime = datetime.combine(date.today(), self.exit_time)
        
        # Calculate total duration in hours
        duration = (exit_datetime - entry_datetime).total_seconds() / 3600
        
        # Apply lunch deduction (30 minutes if lunch_duration > 30)
        lunch_deduction = 0.5 if self.lunch_duration > 30 else 0
        
        return max(0, duration - lunch_deduction)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    amount = Column(Float)
    payment_method = Column(String)  # "cash" or "check"
    payment_date = Column(Date)
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="payments")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    
    # Relationships
    costs = relationship("ProjectCost", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")
    
    @property
    def total_costs(self):
        """Calculate total costs for the project"""
        return sum(cost.amount for cost in self.costs)
    
    @property
    def profit_margin(self):
        """Calculate profit margin based on invoices and costs"""
        total_invoiced = sum(invoice.amount_charged for invoice in self.invoices)
        return total_invoiced - self.total_costs


class ProjectCost(Base):
    __tablename__ = "project_costs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    cost_type = Column(String)  # "material" or "employee"
    description = Column(String)
    amount = Column(Float)
    
    # Relationships
    project = relationship("Project", back_populates="costs")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount_charged = Column(Float)
    invoice_date = Column(Date)
    
    # Relationships
    project = relationship("Project", back_populates="invoices")


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"

    id = Column(Integer, primary_key=True, index=True)
    supplier = Column(String)
    description = Column(String)
    amount = Column(Float)
    due_date = Column(Date)
    payment_method = Column(String)
    category = Column(String)
    status = Column(String)  # "pending" or "paid"
    notes = Column(Text, nullable=True)


class PaidAccount(Base):
    __tablename__ = "paid_accounts"

    id = Column(Integer, primary_key=True, index=True)
    supplier = Column(String)
    amount_paid = Column(Float)
    payment_date = Column(Date)
    payment_method = Column(String)
    check_number = Column(String, nullable=True)
    check_bank = Column(String, nullable=True)
    payment_proof = Column(String, nullable=True)
    notes = Column(Text, nullable=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    expense_date = Column(Date)
    category = Column(String)
    payment_method = Column(String)
    notes = Column(Text, nullable=True)
