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

def main():
    """Executa o script de correção da base de dados."""
    engine = get_postgres_engine()
    if engine is None:
        print("Não foi possível conectar à base de dados. Verifique o seu ficheiro secrets.toml.")
        return

    with engine.connect() as conn:
        try:
            print("A iniciar a correção da base de dados...")
            
            # Inicia uma transação
            with conn.begin():
                # 1. Criar backup
                print("Passo 1: A criar uma cópia de segurança da tabela 'usuarios'...")
                conn.execute(sqlalchemy.text("CREATE TABLE usuarios_backup AS SELECT * FROM usuarios;"))
                print("Cópia de segurança 'usuarios_backup' criada com sucesso.")

                # 2. Corrigir os dados
                print("Passo 2: A corrigir os dados na tabela 'usuarios'...")
                update_query = sqlalchemy.text("""
                UPDATE usuarios
                SET 
                    "CPF" = "EMAIL",
                    "EMAIL" = "NOME",
                    "NOME" = "ID"
                WHERE "ID" IS NOT NULL AND "ID" ~ E'^\\D';
                """
                )
                result = conn.execute(update_query)
                print(f"{result.rowcount} linhas foram atualizadas.")

            print("\nCorreção da base de dados concluída com sucesso!")
            print("Por favor, verifique os dados na sua tabela 'usuarios'.")
            print("Se tudo estiver correto, pode apagar a tabela 'usuarios_backup' manualmente.")

        except Exception as e:
            print(f"\nOcorreu um erro: {e}")
            print("As alterações foram revertidas (rollback). A sua base de dados não foi alterada.")

if __name__ == "__main__":
    main()