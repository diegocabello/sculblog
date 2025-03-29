db_loc              = os.path.abspath(os.path.join('/', 'srv', 'http', 'database'))

@contextmanager
def db_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def send_query(conn, query, params=None):
    try:
        with conn:
            results = execute_query(conn, query, params)
            if results:
                for row in results:
                    for column, value in row.items():
                        print(f"{column}: \n\t{value} \n")
                    print("\n-----\n")
            else:
                print("No results returned.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    
def execute_single_query(conn, query, params=None):
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def insert_row(conn, table, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    try:
        with conn:
            conn.execute(query, tuple(data.values()))
        return True
    except sqlite3.Error as e:
        print(f"Insert error: {e}")
        return False

value_in_column = lambda conn, table, column, target: bool(execute_single_query(conn, f"SELECT 1 FROM {table} WHERE {column} = ?", (target,)))

def update_row(conn, table, where_column, where_value, update_columns):
    if not update_columns:
        return
    
    query = f"UPDATE {table} SET {', '.join(f'{col} = ?' for col in update_columns)} WHERE {where_column} = ?"
    
    try:
        conn.cursor().execute(query, (*update_columns.values(), where_value))
        conn.commit()
        #return cursor.rowcount
    except sqlite3.Error as e:
        print(f"Update error: {e}")

def execute_query(conn, query, params=None):
    try:
        if conn.row_factory != sqlite3.Row:
            conn.row_factory = sqlite3.Row
        with conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

