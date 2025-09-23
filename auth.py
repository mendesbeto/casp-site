import bcrypt
import sqlalchemy
import streamlit as st

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados PostgreSQL usando SQLAlchemy."""
    try:
        db_url = st.secrets["database"]["url"]
        engine = sqlalchemy.create_engine(db_url)
        return engine.connect()
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def hash_password(password: str) -> str:
    """Gera um hash seguro para a senha."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash."""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_user_by_email(email: str):
    """Busca um usuário pelo email no banco de dados."""
    conn = get_db_connection()
    if conn is None: return None
    try:
        query = sqlalchemy.text('SELECT * FROM usuarios WHERE "EMAIL" = :email')
        result = conn.execute(query, {"email": email})
        return result.mappings().first()
    finally:
        if conn: conn.close()

def get_user_by_id(user_id: int):
    """Busca um usuário pelo ID no banco de dados."""
    conn = get_db_connection()
    if conn is None: return None
    try:
        query = sqlalchemy.text('SELECT * FROM usuarios WHERE "ID" = :user_id')
        result = conn.execute(query, {"user_id": user_id})
        return result.mappings().first()
    finally:
        if conn: conn.close()

def insert_record(table_name, record_dict):
    """Insere um novo registro em uma tabela."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        columns = ', '.join(record_dict.keys())
        sanitized_keys = [key.strip('"') for key in record_dict.keys()]
        placeholders = ', '.join([f":{key}" for key in sanitized_keys])
        query = sqlalchemy.text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
        
        sanitized_dict = {key.strip('"'): value for key, value in record_dict.items()}
        
        with conn.begin():
            conn.execute(query, sanitized_dict)
        return True
    except Exception as e:
        print(f"Erro ao inserir registro: {e}")
        return False
    finally:
        if conn: conn.close()

def get_max_id(table_name, id_column):
    """Pega o ID máximo de uma tabela."""
    conn = get_db_connection()
    if conn is None: return 0
    try:
        query = sqlalchemy.text(f"SELECT MAX({id_column}) FROM {table_name}")
        max_id = conn.execute(query).scalar()
        return max_id if max_id is not None else 0
    except Exception as e:
        print(f"Erro ao buscar ID máximo: {e}")
        return 0
    finally:
        if conn: conn.close()

def update_record(table_name, record_dict, where_clause):
    """Atualiza um registro em uma tabela."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        set_clause_list = []
        where_clause_list = []
        params = {}

        for key, value in record_dict.items():
            sanitized_key = key.strip('"')
            set_clause_list.append(f'{key} = :{sanitized_key}')
            params[sanitized_key] = value

        for key, value in where_clause.items():
            sanitized_key = key.strip('"')
            where_clause_list.append(f'{key} = :{sanitized_key}_where')
            params[f'{sanitized_key}_where'] = value

        set_clause = ", ".join(set_clause_list)
        where_keys = " AND ".join(where_clause_list)
        
        query = sqlalchemy.text(f"UPDATE {table_name} SET {set_clause} WHERE {where_keys}")
        
        with conn.begin():
            conn.execute(query, params)
        return True
    except Exception as e:
        print(f"Erro ao atualizar registro: {e}")
        return False
    finally:
        if conn: conn.close()

def delete_record(table_name, where_clause):
    """Deleta um registro de uma tabela."""
    conn = get_db_connection()
    if conn is None: return False
    try:
        where_clause_list = []
        params = {}

        for key, value in where_clause.items():
            sanitized_key = key.strip('"')
            where_clause_list.append(f'{key} = :{sanitized_key}')
            params[sanitized_key] = value

        where_keys = " AND ".join(where_clause_list)
        query = sqlalchemy.text(f"DELETE FROM {table_name} WHERE {where_keys}")
        
        with conn.begin():
            conn.execute(query, params)
        return True
    except Exception as e:
        print(f"Erro ao deletar registro: {e}")
        return False
    finally:
        if conn: conn.close()