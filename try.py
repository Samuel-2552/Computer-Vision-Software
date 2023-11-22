import sqlite3


conn = sqlite3.connect('labelimg.db')
cursor = conn.cursor()

# Create the labelimg table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS labelimg (
        window INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    INSERT INTO labelimg (window)
    VALUES (0)
''')

cursor.execute('''
            UPDATE labelimg
            SET window = 0
            WHERE rowid = 1
        ''')
conn.commit()

