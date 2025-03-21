# Financial Management

## Overview

The financial management module is designed to track accounts payable, paid accounts, and expenses. It includes features for monitoring payment methods, categorizing expenses, and generating financial reports.

## Features

### Accounts Payable Tracking

- Record bills and invoices to be paid
- Track supplier information
- Monitor due dates
- Categorize payables
- Support different payment methods

### Paid Accounts Management

- Record payments made to suppliers
- Track payment method details
- Monitor payment history
- Link payments to accounts payable

### Expense Tracking

- Record company expenses by category
- Track payment methods
- Monitor monthly expenses
- Analyze expense patterns

### Financial Reporting

- Generate accounts payable reports
- View paid accounts by date range
- Analyze expenses by category
- Monitor payment methods
- Create payment forecasts

## Database Schema

### AccountsPayable Table

- `id`: Integer (Primary Key)
- `supplier`: String
- `description`: String
- `amount`: Float
- `issue_date`: Date
- `due_date`: Date
- `payment_method`: String
- `category`: String
- `notes`: String
- `status`: String (pending, paid)
- `created_at`: DateTime

### PaidAccount Table

- `id`: Integer (Primary Key)
- `supplier`: String
- `description`: String
- `amount_paid`: Float
- `payment_date`: Date
- `payment_method`: String (cash, check)
- `check_number`: String (nullable)
- `check_bank`: String (nullable)
- `category`: String
- `notes`: String
- `created_at`: DateTime

### Expense Table

- `id`: Integer (Primary Key)
- `description`: String
- `amount`: Float
- `expense_date`: Date
- `category`: String
- `payment_method`: String
- `notes`: String
- `created_at`: DateTime

## Workflow

1. **Record Accounts Payable**: Enter bills and invoices to be paid
   - Record supplier and amount
   - Set due date
   - Categorize the payable
   - Specify payment method
2. **Process Payments**: Record payments made to suppliers
   - Enter payment details
   - Specify payment method and details
   - Link to accounts payable if applicable
3. **Track Expenses**: Record company expenses
   - Enter expense details
   - Categorize the expense
   - Specify payment method
4. **Generate Reports**: Create financial reports for analysis
   - Accounts payable reports
   - Paid accounts reports
   - Expense reports by category
   - Payment method analysis

## Implementation Details

### Payment Methods

- Cash: Simple record of cash payment
- Check: Record check number and bank for tracking purposes

### Expense Categories

Common expense categories include:
- Rent
- Utilities
- Office Supplies
- Tools and Equipment
- Vehicle Expenses
- Insurance
- Taxes
- Miscellaneous

### Financial Reports

- **Accounts Payable Report**: Lists all pending bills with due dates
- **Paid Accounts Report**: Shows all payments made within a date range
- **Monthly Expense Report**: Analyzes expenses by category
- **Payment Method Report**: Breaks down payments by method
- **Payment Forecast**: Projects upcoming payments based on due dates

### Payment Tracking

- Each payment is recorded with:
  - Date
  - Amount
  - Supplier
  - Payment method
  - Category
  - Notes
- Payments can be linked to accounts payable to maintain a complete financial history
