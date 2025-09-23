import sqlalchemy
import toml

SECRETS_PATH = '.streamlit/secrets.toml'

def get_postgres_engine():
    """Cria um engine de conexão com o PostgreSQL usando as credenciais dos secrets."""
    try:
        secrets = toml.load(SECRETS_PATH)
        db_url = secrets["database"]["url"]
        if 'sslmode' not in db_url:
            db_url += "?sslmode=require"
        return sqlalchemy.create_engine(db_url)
    except Exception as e:
        print(f"Erro ao ler secrets ou criar engine: {e}")
        return None

def inspect_postgres_table_schema(engine, table_name):
    """Inspeciona o esquema de uma tabela no PostgreSQL."""
    if engine is None:
        return
    try:
        with engine.connect() as conn:
            inspector = sqlalchemy.inspect(engine)
            columns = inspector.get_columns(table_name)
            if not columns:
                print(f"Tabela '{table_name}' não encontrada no banco de dados PostgreSQL.")
                return
            print(f"Esquema da tabela '{table_name}' no PostgreSQL:")
            for col in columns:
                print(f"  - Coluna: {col['name']} (Tipo: {col['type']})")
    except Exception as e:
        print(f"Erro ao inspecionar o esquema no PostgreSQL: {e}")

if __name__ == "__main__":
    print("--- INSPECIONANDO ESQUEMA DO POSTGRESQL ---")
    pg_engine = get_postgres_engine()
    tables = ['usuarios', 'institucional', 'convenios', 'noticias', 'eventos', 'receitas', 'despesas', 'parceiros', 'servicos', 'beneficios', 'comentarios', 'contatos', 'log_atividades', 'faq', 'classificados', 'financas']
    for table in tables:
        inspect_postgres_table_schema(pg_engine, table)
        print("\n")
    print("--- INSPEÇÃO CONCLUÍDA ---")