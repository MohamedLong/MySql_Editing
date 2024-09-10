# MySQL Column Management Flask App

This Flask application allows users to manage MySQL database columns, including adding, updating, and deleting columns in specified tables. It also automatically backs up the database before any changes are made.

## Features

- **Add Column**: Add new columns to all tables in the database with customizable attributes like datatype, length, allowing NULL values, and default values.
- **Update Column**: Rename an existing column in a specified table.
- **Delete Column**: Delete a column from a specified table.
- **Automatic Database Backup**: Automatically backs up the MySQL database before any modification (add, update, or delete operation).

## Prerequisites

- Python 3.x
- Flask
- PyMySQL
- MySQL server
- `mysqldump` utility installed for database backup

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/mysql-column-management-app.git
    cd mysql-column-management-app
2. Create a virtual environment (optional but recommended):
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install the required dependencies:
    pip install -r requirements.txt


##  Usage
- **Add Column**
    1. Navigate to the home page.
    2. Fill in the form with your MySQL connection details, the column name, datatype, length, and other parameters.
    3. Click the "Add Column" button.
    4. The application will add the column to all tables with the specified suffix (if any) and display the results.
- **Update Column**
    1. Click on the "Update Column" section.
    2. Enter the MySQL connection details, the table name, the old column name, and the new column name.
    3. Click the "Update Column" button to rename the column.
- **Delete Column**
    1. Click on the "Delete Column" section.
    2. Fill in the form with the MySQL connection details, the table name, and the column name to delete.
    3. Click the "Delete Column" button to delete the column.


