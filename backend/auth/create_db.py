import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='9912129398',
        database='postgres'
    )
    
    # Set autocommit mode
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Create cursor
    cur = conn.cursor()
    
    # Create database
    cur.execute('CREATE DATABASE "AutoJobApply"')
    
    print('✅ Database AutoJobApply created successfully')
    
    # Close connections
    cur.close()
    conn.close()
    
except psycopg2.errors.DuplicateDatabase:
    print('✅ Database AutoJobApply already exists')
except Exception as e:
    print(f'❌ Error creating database: {e}')
