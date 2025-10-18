import pymysql

# Database connection parameters
config = {
    'host': 'db.fr-pari1.bengt.wasmernet.com',
    'port': 10272,
    'user': '4026b4397ea98000e7b309285c82',
    'password': '068f4026-b43a-7014-8000-68afb12126f7',
    'database': 'db_ashique'
}

try:
    # Create connection
    connection = pymysql.connect(**config)
    print("Database connection successful!")
    
    # Create cursor
    cursor = connection.cursor()
    
    # Execute a simple query
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    if version:
        print(f"Database version: {version[0]}")
    else:
        print("Database version: Unknown")
    
    # Close connections
    cursor.close()
    connection.close()
    print("Database connection test completed.")
    
except Exception as e:
    print(f"Error connecting to database: {e}")