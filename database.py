import sqlite3
from datetime import datetime

def create_database():
    # Connect (or create) a database
    conn = sqlite3.connect('ED_CODE.db')
    cursor = conn.cursor()

    # create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            modification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # close connection
    conn.close()

def save_new_project_in_the_database(path):
    conn = sqlite3.connect('ED_CODE.db')
    cursor = conn.cursor()

    try:
        # Save the folder
        cursor.execute('''
            INSERT INTO folders (path) VALUES (?)
        ''', (path,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: The path already exists in the database.")
        return False
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

def update_modification_date(path):
    # Conectar a la base de datos
    conn = sqlite3.connect('ED_CODE.db')
    cursor = conn.cursor()

    try:
        # Actualizar el modification_date al tiempo actual
        cursor.execute('''
            UPDATE folders
            SET modification_date = ?
            WHERE path = ?
        ''', (datetime.now(), path))  # Utiliza la fecha y hora actual

        # Confirmar los cambios
        conn.commit()

        # Verificar si se modificó alguna fila
        if cursor.rowcount == 0:
            print("No se encontró el path en la base de datos.")
            return False  # Indica que no se encontró el path para actualizar

        return True  # Indica que se realizó la actualización
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False  # Indica que hubo un error
    finally:
        # Cerrar la conexión
        conn.close()

def get_all_the_folders_in_the_database():
    conn = sqlite3.connect('ED_CODE.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM folders ORDER BY modification_date DESC')
    folders = cursor.fetchall()


    conn.close()
    return folders

def delete_folder_in_database(path):
    # Connect to database
    conn = sqlite3.connect('ED_CODE.db')
    cursor = conn.cursor()

    try:
        # Run the delete query
        cursor.execute('''
            DELETE FROM folders WHERE path = ?
        ''', (path,))
        conn.commit()

        # Verificar cuántas filas se eliminaron
        return cursor.rowcount > 0
    
    except sqlite3.Error as e:
        print(f"Error al eliminar la carpeta: {e}")
        return False
    finally:
        conn.close()