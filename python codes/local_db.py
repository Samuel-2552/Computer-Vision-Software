import sqlite3


# conn = sqlite3.connect('labelimg.db')
# cursor = conn.cursor()

# # Create the labelimg table if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS labelimg (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         window INTEGER DEFAULT 0
#     )
# ''')

# cursor.execute('''
#     INSERT INTO labelimg (window)
#     VALUES (0)
# ''')

# cursor.execute('''
#             UPDATE labelimg
#             SET window = 0
#             WHERE id = 1
#         ''')
# conn.commit()
conn = sqlite3.connect('labeldetails.db')
cursor = conn.cursor()

# Create the labelimg table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS labeldetails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proj_id INTEGER NOT NULL,
        proj_direct TEXT NOT NULL
    )
''')

# Insert values into the table
cursor.execute('''
    INSERT INTO labeldetails (proj_id, proj_direct) VALUES (?, ?)
''', (1, ''))  # Replace 'your_project_directory_here' with your actual project directory

conn.commit()
conn.close()  # Close the connection after committing changes
