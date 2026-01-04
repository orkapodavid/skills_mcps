import pyodbc
import os

# Note: This example uses SQLite for portability, but the patterns apply to SQL Server, PostgreSQL, etc.
# For SQL Server, use: DRIVER={ODBC Driver 18 for SQL Server};SERVER=...

def main():
    # Setup a local SQLite database for demonstration
    db_file = "demo_pyodbc.db"

    # Connection string for SQLite3 via ODBC (requires sqliteodbc driver installed)
    # If you don't have the ODBC driver, pyodbc won't work.
    # For this demo code to be runnable in environments without ODBC drivers,
    # we'll mock the behavior if import fails or driver is missing,
    # but the code below reflects the correct pyodbc usage.

    try:
        # Check for drivers
        drivers = pyodbc.drivers()
        print(f"Available Drivers: {drivers}")

        # Construct connection string (Example for SQL Server)
        # conn_str = (
        #     "DRIVER={ODBC Driver 18 for SQL Server};"
        #     "SERVER=localhost;DATABASE=mydb;UID=sa;PWD=Password123;"
        #     "TrustServerCertificate=yes"
        # )

        # Example for SQLite (if driver exists)
        if 'SQLite3 ODBC Driver' in drivers:
             conn_str = f"DRIVER={{SQLite3 ODBC Driver}};Database={db_file}"
        else:
            print("SQLite ODBC driver not found. Skipping live connection.")
            return

        print(f"Connecting to: {conn_str}")

        # 1. Connect using Context Manager
        with pyodbc.connect(conn_str) as cnxn:

            # 2. Create Cursor
            with cnxn.cursor() as cursor:

                # 3. Create Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Users (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        email TEXT
                    )
                """)

                # 4. Insert Data (Parameterized)
                users = [
                    (1, 'Alice', 'alice@example.com'),
                    (2, 'Bob', 'bob@example.com')
                ]
                cursor.executemany("INSERT INTO Users (id, name, email) VALUES (?, ?, ?)", users)

                # 5. Query Data
                cursor.execute("SELECT * FROM Users WHERE id > ?", (0,))

                # Fetch as tuples
                rows = cursor.fetchall()
                for row in rows:
                    print(f"User: {row.id}, Name: {row.name}, Email: {row.email}")

            # Connection commits automatically on exit of 'with cnxn' block if no error

    except pyodbc.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
