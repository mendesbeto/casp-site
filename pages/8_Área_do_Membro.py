
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from auth import verify_password, get_user_by_email, get_db_connection
from pdf_utils import gerar_recibo_pdf
from social_utils import display_social_media_links

display_social_media_links()

st.set_page_config(page_title="Área do Membro", layout="centered")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_dados_noticias():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM noticias", conn)
    conn.close()
    df['DATA'] = pd.to_datetime(df['DATA'])
    return df

@st.cache_data
def carregar_tag_follows():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM tag_follows", conn)
    conn.close()
    return df

@st.cache_data
def carregar_dados_institucionais():
    conn = get_db_connection()
    # Carrega a primeira linha da tabela institucional
    dados = pd.read_sql_query("SELECT * FROM institucional LIMIT 1", conn).iloc[0]
    conn.close()
    return dados

def carregar_historico_financeiro(user_id):
    conn = get_db_connection()
    query = "SELECT * FROM financas WHERE USER_ID = ?"
    df_financas = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df_financas

def atualizar_dados_membro(user_id, novos_dados):
    """Atualiza os dados de um membro no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Constrói a query de atualização dinamicamente
        set_clause = ", ".join([f"{key} = ?" for key in novos_dados.keys()])
        params = list(novos_dados.values()) + [user_id]
        query = f"UPDATE usuarios SET {set_clause} WHERE ID = ?"
        
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Erro de banco de dados: {e}")
        return False
    finally:
        conn.close()

def atualizar_ultimo_acesso(user_id):
    """Atualiza o campo ULTIMO_ACESSO para o usuário no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE usuarios SET ULTIMO_ACESSO = ? WHERE ID = ?", (now_str, user_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar último acesso: {e}") # Log para debug
    finally:
        conn.close()

# --- PÁGINAS E LÓGICA DE UI ---
def pagina_login():
    """Exibe o formulário de login para membros."""
    st.header("Login do Associado")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
 
        if submitted:
            user = get_user_by_email(email)

            if user:
                # Verifica se a conta está ativa e se a senha está correta
                if user['STATUS'] == 'ATIVO' and verify_password(senha, user['SENHA_HASH']):
                    last_login_str = user['ULTIMO_ACESSO']
                    atualizar_ultimo_acesso(user['ID'])

                    st.session_state['member_logged_in'] = True
                    st.session_state['member_info'] = dict(user) # Converte sqlite3.Row para dict
                    st.session_state['last_login_for_notifications'] = last_login_str
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos, ou cadastro pendente de aprovação.")
            else:
                st.error("Email ou senha incorretos.")
    
    st.page_link("pages/9_Recuperar_Senha.py", label="Esqueceu a senha?")

def pagina_perfil():
    """Exibe o perfil do membro logado."""
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    user_info = st.session_state['member_info']
    
    st.title(f"Bem-vindo(a), {user_info['NOME'].split(' ')[0]}!")
    
    # --- EXIBIÇÃO DAS NOTIFICAÇÕES ---
    last_login_str = st.session_state.get('last_login_for_notifications')
    if pd.notna(last_login_str) and last_login_str:
        last_login_dt = pd.to_datetime(last_login_str)
        df_noticias = carregar_dados_noticias()
        df_follows = carregar_tag_follows()
        
        tags_seguidas = df_follows[df_follows['USER_ID'] == user_info['ID']]['TAG_NAME'].tolist()
        
        if tags_seguidas:
            novas_noticias = df_noticias[df_noticias['DATA'] > last_login_dt]
            
            def has_followed_tags(row_tags):
                if pd.isna(row_tags): return False
                return any(tag in [t.strip() for t in row_tags.split(',')] for tag in tags_seguidas)
                
            notificacoes = novas_noticias[novas_noticias['TAGS'].apply(has_followed_tags)]
            
            if not notificacoes.empty:
                with st.container(border=True):
                    st.subheader(f"🔔 Novidades em suas tags seguidas ({len(notificacoes)})")
                    for _, noticia in notificacoes.iterrows():
                        st.markdown(f"- **[{noticia['TITULO']}](/Notícias)**")
                st.divider()

    if st.button("Sair"):
        for key in ['member_logged_in', 'member_info', 'edit_mode', 'last_login_for_notifications']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    tab_perfil, tab_financeiro = st.tabs(["👤 Meu Perfil", "💰 Financeiro"])

    with tab_perfil:
        if not st.session_state.edit_mode:
            st.subheader("Seus Dados")
            # Exibe os dados do dicionário user_info
            st.write(f"**Nome Completo:** {user_info.get('NOME', 'Não informado')}")
            st.write(f"**Email:** {user_info.get('EMAIL', 'Não informado')}")
            st.write(f"**CPF:** {user_info.get('CPF', 'Não informado')}")
            st.write(f"**Telefone:** {user_info.get('TELEFONE', 'Não informado')}")
            st.write(f"**Endereço:** {user_info.get('LOGRADOURO', '')}, {user_info.get('NUMERO', '')} - {user_info.get('BAIRRO', '')}")
            st.write(f"**Cidade/Estado:** {user_info.get('CIDADE', '')} - {user_info.get('ESTADO', '')}")
            
            if st.button("Editar Meus Dados", type="primary"):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            st.subheader("Editar Meus Dados")
            with st.form("form_edit_profile"):
                st.info("Altere os campos que desejar e clique em salvar. Email e CPF não podem ser alterados.")
                
                nome = st.text_input("Nome Completo", value=user_info.get('NOME', ''))
                telefone = st.text_input("Telefone", value=user_info.get('TELEFONE', ''))
                cep = st.text_input("CEP", value=user_info.get('CEP', ''))
                logradouro = st.text_input("Logradouro (Rua, Av.)", value=user_info.get('LOGRADOURO', ''))
                numero = st.text_input("Número", value=user_info.get('NUMERO', ''))
                complemento = st.text_input("Complemento", value=user_info.get('COMPLEMENTO', ''))
                bairro = st.text_input("Bairro", value=user_info.get('BAIRRO', ''))
                cidade = st.text_input("Cidade", value=user_info.get('CIDADE', ''))
                estado = st.text_input("Estado", value=user_info.get('ESTADO', ''))
                
                save_button = st.form_submit_button("Salvar Alterações")
                cancel_button = st.form_submit_button("Cancelar")

                if save_button:
                    novos_dados = {
                        "NOME": nome, "TELEFONE": telefone, "CEP": cep, "LOGRADOURO": logradouro, "NUMERO": numero,
                        "COMPLEMENTO": complemento, "BAIRRO": bairro, "CIDADE": cidade, "ESTADO": estado,
                    }
                    if atualizar_dados_membro(user_info['ID'], novos_dados):
                        st.session_state.member_info.update(novos_dados)
                        st.session_state.edit_mode = False
                        st.success("✅ Dados atualizados com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Ocorreu um erro ao atualizar seus dados.")

                if cancel_button:
                    st.session_state.edit_mode = False
                    st.rerun()

    with tab_financeiro:
        st.subheader("Seu Histórico Financeiro")
        historico_df = carregar_historico_financeiro(user_info['ID'])
        institucional = carregar_dados_institucionais()

        if historico_df.empty:
            st.info("Você ainda não possui registros financeiros.")
        else:
            for _, row in historico_df.sort_values(by="DATA_VENCIMENTO", ascending=False).iterrows():
                status = row['STATUS']
                cor = "blue"
                if status == 'PAGO': cor = "green"
                elif status == 'VENCIDO': cor = "red"
                elif status == 'PENDENTE': cor = "orange"

                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    col1.write(f"**Serviço Contratado:** {row['SERVICO_CONTRATADO']}")
                    col1.write(f"**Vencimento:** {pd.to_datetime(row['DATA_VENCIMENTO']).strftime('%d/%m/%Y')}")
                    
                    valor_formatado = f"R$ {row['VALOR']:.2f}".replace('.', ',')
                    col2.metric("Valor", valor_formatado)
                    col2.markdown(f"Status: **<span style='color:{cor};'>{status}</span>**", unsafe_allow_html=True)
                    
                    if status == 'PAGO':
                        pdf_bytes = gerar_recibo_pdf(row, user_info, institucional)
                        col3.download_button(
                            label="📄 Baixar Recibo",
                            data=pdf_bytes,
                            file_name=f"recibo_{row['COBRANCA_ID']}.pdf",
                            mime="application/pdf",
                            key=f"dl_{row['COBRANCA_ID']}",
                            use_container_width=True
                        )

# --- CONTROLE PRINCIPAL DA PÁGINA ---
if 'member_logged_in' not in st.session_state:
    st.session_state['member_logged_in'] = False

if st.session_state['member_logged_in']:
    pagina_perfil()
else:
    pagina_login()
