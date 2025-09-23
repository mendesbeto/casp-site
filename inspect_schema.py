
import sqlite3

SQLITE_DB_PATH = 'casp.db'

def inspect_table_schema(db_path, table_name):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        if not columns:
            print(f"Tabela '{table_name}' não encontrada no banco de dados.")
            return
        print(f"Esquema da tabela '{table_name}':")
        for col in columns:
            print(f"  - Coluna {col[0]}: {col[1]} (Tipo: {col[2]})")
    except sqlite3.Error as e:
        print(f"Erro ao inspecionar o esquema: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_table_schema(SQLITE_DB_PATH, 'usuarios')
