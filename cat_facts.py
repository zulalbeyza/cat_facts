import requests
import sqlite3
import time
import json

# Step 1: API Request with retry logic
url = "https://cat-fact.herokuapp.com/facts"
max_retries = 3
retry_delay = 3  # initial delay in seconds

for attempt in range(max_retries):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            cat_facts = response.json()
        except ValueError:
            print("Error decoding JSON response")
            cat_facts = []
        break
    else:
        print(f"Error: Received status code {response.status_code}, retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        retry_delay *= 2  # Exponential backoff
else:
    print("Failed to retrieve data after several attempts.")
    cat_facts = []

with open('cat_facts.json', 'w') as json_file:
    json.dump(cat_facts, json_file, indent=4)

# Step 2: Create SQLite Database and Table
conn = sqlite3.connect('cat_facts.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS facts (
        id TEXT PRIMARY KEY,
        text TEXT NOT NULL
    )
''')

# Step 3: Insert Data into SQLite Database
for fact in cat_facts:
    cursor.execute('''
        INSERT OR IGNORE INTO facts (id, text) VALUES (?, ?)
    ''', (fact['_id'], fact['text']))

conn.commit()

# Step 4: Retrieve and Display Data
cursor.execute('SELECT * FROM facts')
rows = cursor.fetchall()

for row in rows:
    print(f'ID: {row[0]} | Fact: {row[1]}')

conn.close()
