import streamlit as st
import pandas as pd
import os
from datetime import datetime
from auth import verify_password
from pdf_utils import gerar_recibo_pdf

st.set_page_config(page_title="Área do Membro", layout="centered")

# --- FUNÇÕES ---
def carregar_usuarios():
    """Carrega o arquivo de usuários."""
    filepath = 'data/usuarios.csv'
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath)

@st.cache_data
def carregar_dados_noticias():
    filepath = 'data/noticias.csv'
    if not os.path.exists(filepath):
        return pd.DataFrame()
    df = pd.read_csv(filepath)
    df['DATA'] = pd.to_datetime(df['DATA'])
    return df

@st.cache_data
def carregar_tag_follows():
    """Carrega os dados de tags seguidas."""
    filepath = 'data/tag_follows.csv'
    return pd.read_csv(filepath) if os.path.exists(filepath) else pd.DataFrame()

@st.cache_data
def carregar_dados_institucionais():
    return pd.read_csv('data/institucional.csv').iloc[0]

def carregar_historico_financeiro(user_id):
    """Carrega o histórico financeiro de um usuário específico."""
    filepath = 'data/financas.csv'
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        # Se o arquivo não existir, cria com os cabeçalhos corretos
        cols = ['COBRANCA_ID','USER_ID','SERVICO_CONTRATADO','VALOR','DATA_EMISSAO','DATA_VENCIMENTO','DATA_PAGAMENTO','DOCUMENTO_URL','VALOR_PAGO','STATUS','OBSERVACOES']
        pd.DataFrame(columns=cols).to_csv(filepath, index=False)
        return pd.DataFrame()
    
    df_financas = pd.read_csv(filepath)
    return df_financas[df_financas['USER_ID'] == user_id]

def atualizar_dados_membro(user_id, novos_dados):
    """Atualiza os dados de um membro no arquivo CSV."""
    filepath = 'data/usuarios.csv'
    df_usuarios = carregar_usuarios()
    
    user_index = df_usuarios[df_usuarios['ID'] == user_id].index
    
    if not user_index.empty:
        for key, value in novos_dados.items():
            df_usuarios.loc[user_index, key] = value
        
        df_usuarios.to_csv(filepath, index=False)
        return True
    return False


def pagina_login():
    """Exibe o formulário de login para membros."""
    st.header("Login do Associado")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
 
        if submitted:
            df_usuarios = carregar_usuarios()
            if df_usuarios.empty:
                st.error("Nenhum usuário cadastrado.")
                return
 
            # Garante que a coluna de email seja do tipo string para evitar erros
            df_usuarios['EMAIL'] = df_usuarios['EMAIL'].astype(str)
            # Procura o usuário pelo email
            user_data = df_usuarios[df_usuarios['EMAIL'].str.lower() == email.lower()]
 
            if not user_data.empty:
                user = user_data.iloc[0]
                # Verifica se a conta está ativa e se a senha está correta
                if user['STATUS'] == 'ATIVO' and verify_password(senha, user['SENHA_HASH']):
                    # --- LÓGICA DE ÚLTIMO ACESSO ---
                    last_login_str = user.get('ULTIMO_ACESSO')
                    df_usuarios.loc[df_usuarios['ID'] == user['ID'], 'ULTIMO_ACESSO'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df_usuarios.to_csv('data/usuarios.csv', index=False)

                    st.session_state['member_logged_in'] = True
                    st.session_state['member_info'] = user.to_dict()
                    st.session_state['last_login_for_notifications'] = last_login_str
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos, ou cadastro pendente de aprovação.")
            else:
                st.error("Email ou senha incorretos.")
    
    st.page_link("pages/9_Recuperar_Senha.py", label="Esqueceu a senha?")

def pagina_perfil():
    """Exibe o perfil do membro logado."""
    # Inicializa o modo de edição se não existir no estado da sessão
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
        # Limpa todas as chaves de sessão relacionadas ao membro para um logout completo
        for key in ['member_logged_in', 'member_info', 'edit_mode', 'last_login_for_notifications']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Se NÃO estiver em modo de edição, mostra os dados e o botão para editar
    tab_perfil, tab_financeiro = st.tabs(["👤 Meu Perfil", "💰 Financeiro"])

    with tab_perfil:
        if not st.session_state.edit_mode:
            st.subheader("Seus Dados")
            st.write(f"**Nome Completo:** {user_info['NOME']}")
            st.write(f"**Email:** {user_info['EMAIL']}")
            st.write(f"**CPF:** {user_info['CPF']}")
            st.write(f"**Endereço:** {user_info.get('LOGRADOURO', '')}, {user_info.get('NUMERO', '')} - {user_info.get('BAIRRO', '')}")
            st.write(f"**Cidade/Estado:** {user_info.get('CIDADE', '')} - {user_info.get('ESTADO', '')}")
            
            if st.button("Editar Meus Dados", type="primary"):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            st.subheader("Editar Meus Dados")
            with st.form("form_edit_profile"):
                st.info("Altere os campos que desejar e clique em salvar. Email e CPF não podem ser alterados.")
                
                nome = st.text_input("Nome Completo", value=user_info['NOME'])
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
                        "NOME": nome, "CEP": cep, "LOGRADOURO": logradouro, "NUMERO": numero,
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