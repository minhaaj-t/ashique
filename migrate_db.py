import pymysql
from app import app, db, Category, Product

# Database connection parameters from app.py
config = {
    'host': 'db.fr-pari1.bengt.wasmernet.com',
    'port': 10272,
    'user': '4026b4397ea98000e7b309285c82',
    'password': '068f4026-b43a-7014-8000-68afb12126f7',
    'database': 'db_ashique'
}

def add_category_column():
    """Add category_id column to existing product table"""
    try:
        # Create connection
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # Check if category_id column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'product' 
            AND COLUMN_NAME = 'category_id'
        """, (config['database'],))
        
        result = cursor.fetchone()
        
        if not result:
            print("Adding category_id column to product table...")
            # Add category_id column
            cursor.execute("ALTER TABLE product ADD COLUMN category_id INTEGER")
            # Add foreign key constraint
            cursor.execute("ALTER TABLE product ADD CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category(id)")
            connection.commit()
            print("Category column added successfully!")
        else:
            print("Category column already exists.")
            
        # Check if category table exists, if not create it
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'category'
        """, (config['database'],))
        
        result = cursor.fetchone()
        
        if not result:
            print("Creating category table...")
            cursor.execute("""
                CREATE TABLE category (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT
                )
            """)
            connection.commit()
            print("Category table created successfully!")
        else:
            print("Category table already exists.")
            
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error during migration: {e}")

def create_default_categories():
    """Create default categories if they don't exist"""
    with app.app_context():
        # Check if categories exist
        if not Category.query.first():
            print("Creating default categories...")
            categories = [
                Category(name='Engagement Rings', description='Beautiful engagement rings for your special moment'),
                Category(name='Fine Jewelry', description='Elegant pieces for special occasions'),
                Category(name='Royal Collection', description='Exclusive pieces inspired by royal elegance'),
                Category(name='Gift Sets', description='Perfect curated gifts for your loved ones')
            ]
            for category in categories:
                db.session.add(category)  # type: ignore
            db.session.commit()  # type: ignore
            print("Default categories created successfully!")
        else:
            print("Categories already exist.")

if __name__ == '__main__':
    add_category_column()
    create_default_categories()