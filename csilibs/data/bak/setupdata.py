import sqlite3, json, os

db_filename = 'sites_userenum.db'

# Get the current working directory
current_directory = os.getcwd()

# List all files and folders in the current directory
site_dir = os.path.join(current_directory,'sites')
directory_contents = os.listdir(site_dir)

for s in directory_contents:
    sites = s.removesuffix('.json')
    with sqlite3.connect(db_filename) as conn:

        cursor = conn.cursor()


        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {sites} (
                            id INTEGER PRIMARY KEY,
                            site_name TEXT,
                            site_url TEXT,
                            method TEXT,
                            type TEXT,
                            key TEXT,
                            onoff TEXT
                        )''')
        with open(os.path.join(site_dir, s), 'r') as json_file:
            # Load the JSON data into a Python dictionary
            data = json.load(json_file)
        print("********",s)
        for d  in data:
            cursor.execute(f"INSERT INTO {sites} (site_name, site_url, method, type, key, onoff) VALUES (?, ?, ?, ?, ?, ?)", (d['site_name'], d['surl'], d['method'], d['type'], d['key'], d['onoff']))

            # cursor.execute("UPDATE employees SET title = 'Supervisor' WHERE name = 'John Doe'")
            # cursor.execute("DELETE FROM employees WHERE name = 'John Doe'")

            # cursor.execute("SELECT * FROM employees")
            # rows = cursor.fetchall()
            # for row in rows:
            #     print(row)


            conn.commit()

    # The connection is automatically closed when exiting the 'with' block.
    # You don't need to explicitly call conn.close().
