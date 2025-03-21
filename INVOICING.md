# Project Invoicing

## Overview

The project invoicing module is designed to manage construction projects, track costs, and generate invoices. It includes features for calculating profit margins and monitoring project status.

## Features

### Project Management

- Add, edit, and delete projects
- Track project information:
  - Project name
  - Client details
  - Start and end dates
  - Status (in progress, completed, etc.)
  - Description and notes

### Project Cost Tracking

- Record material costs
- Track labor costs (integrated with work log entries)
- Calculate total project costs
- Monitor cost breakdown by category

### Invoicing

- Generate invoices for projects
- Track invoice status (draft, sent, paid)
- Record payment details
- Calculate remaining balance

### Profit Margin Calculation

- Calculate project revenue (from invoices)
- Track total project costs
- Compute profit margin and percentage
- Analyze project profitability

## Database Schema

### Project Table

- `id`: Integer (Primary Key)
- `name`: String
- `client`: String
- `start_date`: Date
- `end_date`: Date (nullable)
- `status`: String
- `description`: String
- `notes`: String
- `created_at`: DateTime

### ProjectCost Table

- `id`: Integer (Primary Key)
- `project_id`: Integer (Foreign Key to Project)
- `description`: String
- `amount`: Float
- `cost_date`: Date
- `cost_type`: String (material, other)
- `notes`: String
- `created_at`: DateTime

### Invoice Table

- `id`: Integer (Primary Key)
- `project_id`: Integer (Foreign Key to Project)
- `invoice_number`: String
- `amount`: Float
- `issue_date`: Date
- `due_date`: Date
- `status`: String (draft, sent, paid)
- `payment_date`: Date (nullable)
- `payment_method`: String (nullable)
- `notes`: String
- `created_at`: DateTime

## Workflow

1. **Create Project**: Enter project information including client details
2. **Track Costs**: Record material costs and other expenses
   - Labor costs are automatically tracked through work log entries
   - System calculates total project costs
3. **Generate Invoice**: Create invoice for the project
   - Enter invoice details
   - Set invoice status
   - Record payment when received
4. **Monitor Profitability**: Analyze project profitability
   - Calculate profit margin
   - Review cost breakdown
   - Evaluate project performance

## Implementation Details

### Cost Tracking

- Material costs: Entered directly as project costs
- Labor costs: Calculated from work log entries associated with the project
- Total cost = Material costs + Labor costs + Other costs

### Invoice Generation

- Invoice number: Automatically generated or manually entered
- Invoice amount: Entered based on project agreement
- Invoice status: Updated as the invoice progresses through the lifecycle

### Profit Calculation

- Revenue = Sum of all invoice amounts for the project
- Cost = Sum of all project costs (materials, labor, other)
- Profit = Revenue - Cost
- Profit Margin (%) = (Profit / Revenue) × 100

### Project Status Tracking

- Project status options:
  - Planning
  - In Progress
  - On Hold
  - Completed
  - Cancelled
- Status updates trigger notifications and reporting updates
