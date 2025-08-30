#!/usr/bin/env python3
"""
Create database tables for Auto Job Apply System
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_tables():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='9912129398',
            database='AutoJobApply'
        )
        
        # Set autocommit mode
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Create cursor
        cur = conn.cursor()
        
        # Read and execute SQL file
        with open('db/init/01_create_tables.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            
        # Execute the SQL script
        cur.execute(sql_script)
        
        print('✅ Database tables created successfully!')
        
        # Verify tables were created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f'\n📋 Created {len(tables)} tables:')
        for table in tables:
            print(f'   - {table[0]}')
        
        # Close connections
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating database tables: {e}')
        return False

if __name__ == "__main__":
    create_tables()
