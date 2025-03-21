# Payroll Management

## Overview

The payroll management module is designed to track employee hours, calculate payments, and maintain payment records. It includes features for tracking lunch breaks and different payment methods.

## Features

### Employee Management

- Add, edit, and delete employees
- Track employee information:
  - Name
  - Hourly rate
  - Position
  - Contact information

### Work Log Entry

- Record daily work hours for each employee
- Track entry and exit times
- Monitor lunch duration (with automatic 30-minute deduction for lunch breaks over 30 minutes)
- Calculate total hours worked
- Associate work hours with specific projects

### Payroll Processing

- Calculate weekly payroll based on recorded hours
- Support different payment methods:
  - Cash
  - Check (with check number and bank tracking)
- Record payment date and notes
- View payment history

### Payroll Reports

- Generate payroll reports by date range
- View hours worked by employee
- Analyze payment methods
- Export reports for accounting purposes

## Database Schema

### Employee Table

- `id`: Integer (Primary Key)
- `name`: String
- `position`: String
- `hourly_rate`: Float
- `contact_info`: String
- `created_at`: DateTime

### WorkLog Table

- `id`: Integer (Primary Key)
- `employee_id`: Integer (Foreign Key to Employee)
- `project_id`: Integer (Foreign Key to Project)
- `work_date`: Date
- `entry_time`: Time
- `exit_time`: Time
- `lunch_duration`: Integer (minutes)
- `hours_worked`: Float
- `notes`: String
- `created_at`: DateTime

### Payment Table

- `id`: Integer (Primary Key)
- `employee_id`: Integer (Foreign Key to Employee)
- `amount`: Float
- `payment_date`: Date
- `payment_method`: String (cash, check)
- `check_number`: String (nullable)
- `check_bank`: String (nullable)
- `notes`: String
- `created_at`: DateTime

## Workflow

1. **Add Employees**: Enter employee information including hourly rate
2. **Record Work Hours**: Enter daily work hours for each employee
   - Record entry time, exit time, and lunch duration
   - System calculates total hours worked
   - Associate hours with specific projects for cost tracking
3. **Process Payroll**: Calculate and record payments
   - Select date range (typically weekly)
   - Review hours worked
   - Calculate payment amount
   - Select payment method and enter details
   - Record payment
4. **Generate Reports**: Create reports for analysis and accounting
   - Payroll reports by date range
   - Hours worked by employee
   - Payment method analysis

## Implementation Details

### Work Hours Calculation

- Total hours = (Exit time - Entry time) - Lunch deduction
- Lunch deduction = 30 minutes if lunch_duration > 30 minutes, otherwise 0

### Payroll Calculation

- Payment amount = Hours worked × Hourly rate
- Weekly payroll typically calculated on Fridays for the past week

### Payment Methods

- Cash: Simple record of cash payment
- Check: Record check number and bank for tracking purposes
