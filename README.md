# Construction ERP

A comprehensive ERP system for construction companies, featuring payroll management, project invoicing, financial tracking, and interactive data visualization.

## Features

- **Interactive Dashboard**: Visual overview of key metrics with charts and graphs
- **Employee Management**: Track employees and their hourly rates
- **Work Log Entry**: Record daily hours with lunch break tracking
- **Payroll Processing**: Calculate weekly payroll with payment method tracking
- **Project Management**: Track projects, costs, and profit margins
- **Invoicing**: Generate invoices for projects
- **Financial Management**: Handle accounts payable, paid accounts, and expenses
- **Data Validation**: Client and server-side validation with real-time feedback
- **Confirmation Dialogs**: Prevent accidental data deletion or modification
- **Data Visualization**: Interactive charts for financial analysis
- **Reports**: Generate various reports for payroll, projects, and finances

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML with Jinja2 templates and Bootstrap
- **Validation**: Client-side (JavaScript) and server-side (Python) validation
- **Data Visualization**: Chart.js
- **Deployment**: Gunicorn

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd construction_erp
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```
uvicorn app:app --reload
```

The application will be available at http://localhost:8000

### Production Mode

```
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Project Structure

```
construction_erp/
├── app.py               # Main FastAPI application with routes
├── models.py            # SQLAlchemy database models
├── database.py          # Database connection and session management
├── validation.py        # Server-side validation module
├── templates/           # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── employees.html   # Employee management page
│   ├── worklogs.html    # Work log entry page
│   ├── payroll.html     # Payroll processing page
│   ├── projects.html    # Project management page
│   ├── invoices.html    # Invoicing page
│   ├── financials.html  # Financial management page
│   └── reports.html     # Reports page
├── static/              # Static files
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       ├── script.js    # Custom JavaScript
│       └── validation.js # Client-side validation and confirmation dialogs
├── requirements.txt     # Dependencies
├── PLAN.md              # Project overview and requirements
├── PAYROLL.md           # Payroll feature details
├── INVOICING.md         # Project invoicing feature details
├── FINANCIALS.md        # Financial management feature details
└── README.md            # Setup and deployment instructions
```

## Usage

1. **Dashboard**: View key metrics and visualizations on the home page
2. **Employee Management**: Add employees and their hourly rates
3. **Work Log Entry**: Record daily hours for employees (typically done on Fridays for the past week)
4. **Payroll Processing**: Calculate and process weekly payroll
5. **Project Management**: Create projects and track costs
6. **Invoicing**: Generate invoices for projects
7. **Financial Management**: Track accounts payable, paid accounts, and expenses
8. **Reports**: Generate various reports for analysis

## Data Validation

The system includes comprehensive validation to ensure data integrity:

### Client-side Validation
- Real-time feedback as users type in form fields
- Visual indicators for valid/invalid inputs
- Prevents form submission with invalid data

### Server-side Validation
- Validates all data before saving to the database
- Returns specific error messages for each field
- Preserves form data when validation fails

### Confirmation Dialogs
- Prevents accidental deletion of important data
- Requires explicit confirmation for critical actions
- Provides clear warnings about potential data loss

## License

This project is licensed under the MIT License - see the LICENSE file for details.
