from flask import Flask, render_template, request, flash, request, redirect, url_for
import pymysql
import os
import datetime
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key required for flashing messages
backup_dir = '/app/downloads'

def connect_to_database(host, user, password, database):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=3306
        )

        backup_file = backup_database(backup_dir, host, database, user, password)
        if backup_file is None:
            print("backup_file to database NOT DONE")
            return None  # If backup fails, abort the operation
        
        print("backup_file to database Done")
        return conn
    except Exception as e:
        print("Error connecting to database:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    success_tables = None
    if request.method == 'POST':
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        database = request.form['database']
        test_column_name = request.form['test_column']
        datatype = request.form['datatype']  # New field for datatype
        length = request.form.get('length', None)  # New field for length, set to None if not provided
        allow_null = 'allow_null' in request.form  # New field for allow_null, boolean value
        default_value = request.form.get('default', None)  # New field for default value, set to None if not provided
        table_suffix = request.form.get('table_suffix')  # Get table suffix or None if not provided

        success_tables = add_column_to_tables(host, user, password, database, test_column_name, datatype, length, allow_null, default_value, table_suffix)

    return render_template('index.html', success_tables=success_tables)

def add_column_to_tables(host, user, password, database, test_column_name, datatype, length, allow_null=False, default_value=None, table_suffix=None):  
    try:
        conn = connect_to_database(host, user, password, database)
        if conn is None:
            flash('Error connecting to the database', 'error')
            return None

        cursor = conn.cursor()

        sql_table_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
        """

        if table_suffix:
            sql_table_query += " AND table_name LIKE %s;"

        cursor.execute(sql_table_query, (database, f'%\_{table_suffix}' if table_suffix else None))
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            sql_alter_query = f"ALTER TABLE {table_name} ADD COLUMN {test_column_name} {datatype}"
            if length is None or length == '':
                length = '255'  # Set length to 255 if it's None or empty string
            if length:
                sql_alter_query += f"({length})"
            if not allow_null:
                sql_alter_query += " NOT NULL"
            if default_value is not None:
                sql_alter_query += f" DEFAULT '{default_value}'"
            print("Executing query:", sql_alter_query)  # Flash the SQL query
            cursor.execute(sql_alter_query)

        conn.commit()
        success_tables = [table[0] for table in tables]
    except Exception as e:
        print("Error:", e)
        flash('An error occurred while adding columns to tables', 'error')
        success_tables = None
    finally:
        cursor.close()
        conn.close()

    return success_tables

@app.route('/delete', methods=['POST'])
def delete_column():
    if request.method == 'POST':
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        database = request.form['database']
        column_name = request.form['column_name']
        table_name = request.form['table_name']

        success = delete_column_from_table(host, user, password, database, table_name, column_name)
        if success:
            return redirect(url_for('index'))  # Redirect to index route
        else:
            return redirect(url_for('index'))  # Redirect to index route with error message


def delete_column_from_table(host, user, password, database, table_name, column_name):
    try:
        conn = connect_to_database(host, user, password, database)
        if conn is None:
            return False

        cursor = conn.cursor()

        sql_delete_query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        cursor.execute(sql_delete_query)

        conn.commit()

        flash(f'DB Backup is done and Successfully deleted column {column_name} from table {table_name}', 'delete_success')  # Flash success message with 'delete_success' category
        return True
    except Exception as e:
        print("Error:", e)
        flash('An error occurred while deleting the column', 'error')  # Flash error message
        return False
    finally:
        cursor.close()
        conn.close()

@app.route('/update', methods=['POST'])
def update_column():
    if request.method == 'POST':
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        database = request.form['database']
        table_name = request.form['table_name']
        old_column_name = request.form['old_column_name']
        new_column_name = request.form['new_column_name']

        success = update_column_name_in_table(host, user, password, database, table_name, old_column_name, new_column_name)
        if success:
            return redirect(url_for('index'))  # Redirect to index route
        else:
            return redirect(url_for('index'))  # Redirect to index route with error message


    return redirect(url_for('index'))

def update_column_name_in_table(host, user, password, database, table_name, old_column_name, new_column_name):
    try:
        conn = connect_to_database(host, user, password, database)
        if conn is None:
            flash('Error connecting to the database', 'error')
            return False

        cursor = conn.cursor()

        # Construct the SQL query to update the column name
        sql_update_query = f"ALTER TABLE `{table_name}` CHANGE `{old_column_name}` `{new_column_name}` VARCHAR(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL;"

        # Execute the SQL query
        cursor.execute(sql_update_query)

        # Commit the changes
        conn.commit()
        
        flash(f"DB Backup is done and Column name updated successfully from '{old_column_name}' to '{new_column_name}'", 'update_success')  # Flash success message with 'update_success' category

        return True
    except Exception as e:
        error_message = f"An error occurred while updating the column name: {e}"
        flash(error_message, 'error')
        print(error_message)  # Print the error for debugging purposes
        return False
    finally:
        cursor.close()
        conn.close()


def backup_database(backup_dir, host, database, user, password):
    try:
        # Generate backup file name with database name
        backup_file = os.path.join(backup_dir, f"{database}.sql")

        # Command to perform the backup
        command = f"mysqldump --host={host} --user={user} --password={password} {database} > {backup_file}"
        print(f"Command to perform the backup: {command}")
        # Execute the backup command
        subprocess.run(command, shell=True, check=True)

        # Rename the backup file with current date
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        new_backup_file = os.path.join(backup_dir, f"{database}_{today_date}.sql")
        os.rename(backup_file, new_backup_file)

        print(f"Database backup saved to {new_backup_file}")
        return new_backup_file  # Return the path of the backup file
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while backing up the database', 'error')  # Flash error message if backup fails
        return None  # Return None if backup fails


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
