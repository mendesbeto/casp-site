import bcrypt
import sqlite3

DB_PATH = 'casp.db'

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Isso permite acessar as colunas pelo nome
    return conn

def hash_password(password: str) -> str:
    """Gera um hash seguro para a senha."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash."""
    # A senha do banco de dados pode não estar em formato de bytes, então codificamos.
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_user_by_email(email: str):
    """Busca um usuário pelo email no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    """Busca um usuário pelo ID no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE USER_ID = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_record(table_name, record_dict):
    """Insere um novo registro em uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        columns = ', '.join(record_dict.keys())
        placeholders = ', '.join(['?'] * len(record_dict))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(record_dict.values()))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao inserir registro: {e}")
        return False
    finally:
        conn.close()

def get_max_id(table_name, id_column):
    """Pega o ID máximo de uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        return max_id if max_id is not None else 0
    except sqlite3.Error as e:
        print(f"Erro ao buscar ID máximo: {e}")
        return 0
    finally:
        conn.close()

def update_record(table_name, record_dict, where_clause):
    """Atualiza um registro em uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in record_dict.keys()])
        params = list(record_dict.values()) + list(where_clause.values())
        where_keys = " AND ".join([f"{key} = ?" for key in where_clause.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_keys}"
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar registro: {e}")
        return False
    finally:
        conn.close()

def delete_record(table_name, where_clause):
    """Deleta um registro de uma tabela."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        where_keys = " AND ".join([f"{key} = ?" for key in where_clause.keys()])
        params = list(where_clause.values())
        query = f"DELETE FROM {table_name} WHERE {where_keys}"
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar registro: {e}")
        return False
    finally:
        conn.close()