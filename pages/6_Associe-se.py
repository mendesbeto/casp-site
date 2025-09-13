
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from social_utils import display_social_media_links
from auth import hash_password, insert_record, get_max_id, get_db_connection
from file_utils import save_uploaded_file
from pdf_utils import gerar_contrato_adesao_pdf

display_social_media_links()
st.set_page_config(page_title="Associe-se", layout="wide")

# --- FUNÇÕES DE BANCO DE DADOS ---
@st.cache_data
def carregar_dados_db(table_name):
    """Carrega uma tabela inteira do banco de dados para um DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados da tabela {table_name}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# --- FUNÇÕES DE CÁLCULO ---
def calcular_preco_plano(servico, plano_key):
    """Calcula o preço final de um plano com base no serviço e no desconto."""
    preco_base = servico['VALOR_MENSAL']
    meses = PLANOS[plano_key]['meses']
    desconto = 0

    if plano_key == "SEMESTRAL":
        desconto = (((servico['CUPOM_SEMESTRAL']/100) * preco_base) * meses)
    elif plano_key == "ANUAL":
        desconto = (((servico['CUPOM_ANUAL']/100) * preco_base) * meses)
    else: # MENSAL
        desconto = servico['CUPOM_MESAL']

    preco_total = (preco_base * meses) - desconto
    return {
        "preco_final": preco_total,
        "economia": desconto,
        "preco_por_mes": preco_total / meses
    }

# --- CONFIGURAÇÕES DOS PLANOS ---
PLANOS = {
    "MENSAL": {"nome": "Mensal", "meses": 1},
    "SEMESTRAL": {"nome": "Semestral", "meses": 6},
    "ANUAL": {"nome": "Anual", "meses": 12}
}

# --- FUNÇÕES DE MANIPULAÇÃO DE DADOS ---
def salvar_novo_membro(dados_membro):
    """Salva os dados do novo membro no banco de dados."""
    new_id = get_max_id('usuarios', 'ID') + 1
    
    dados_membro['ID'] = new_id
    dados_membro['STATUS'] = 'PENDENTE'
    dados_membro['NIVEL_ACESSO'] = 'MEMBRO'
    dados_membro['DATA_CADASTRO'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return insert_record('usuarios', dados_membro)

# --- CARREGAMENTO DOS DADOS ---
institucional = carregar_dados_db('institucional').iloc[0]
servicos = carregar_dados_db('servicos')

# --- LAYOUT DA PÁGINA ---
st.title("📝 Solicitação de Benefícios")
st.write("Siga as etapas abaixo para se tornar um membro e aproveitar todos os nossos benefícios!")

# --- CONTROLE DE ETAPAS ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- ETAPAS DO FORMULÁRIO ---
def step1_selecao():
    st.header("Etapa 1: Escolha seu Serviço e Plano")
    lista_servicos = [f"{row['TIPO_SERVICO']}" for index, row in servicos.iterrows()]
    servico_selecionado_str = st.selectbox("**Primeiro, selecione o serviço desejado:**", lista_servicos)
    
    servico_selecionado_idx = lista_servicos.index(servico_selecionado_str)
    servico_selecionado = servicos.iloc[servico_selecionado_idx]
    st.session_state.form_data['servico_selecionado'] = servico_selecionado.to_dict()

    st.info(f"**Descrição:** {servico_selecionado['DESCRICAO_SERVICO']}")

    if servico_selecionado['VALOR_ADICIONAL'] > 0:
        st.subheader("Dependentes/Adicionais")
        num_adicionais = st.number_input(f"Deseja incluir dependentes? (Custo adicional de R$ {servico_selecionado['VALOR_ADICIONAL']:.2f} por dependente)", min_value=0, step=1)
        st.session_state.form_data['num_adicionais'] = num_adicionais
        
        nomes_adicionais = []
        if num_adicionais > 0:
            for i in range(num_adicionais):
                nomes_adicionais.append(st.text_input(f"Nome do Dependente {i+1}", key=f"add_{i}"))
            st.session_state.form_data['nomes_adicionais'] = ", ".join(nomes_adicionais)
    else:
        st.session_state.form_data['num_adicionais'] = 0
        st.session_state.form_data['nomes_adicionais'] = ""

    st.divider()
    st.subheader("Agora, escolha a forma de pagamento:")

    cols = st.columns(len(PLANOS))
    for i, (plano_key, plano_info) in enumerate(PLANOS.items()):
        with cols[i]:
            with st.container(border=True):
                st.subheader(plano_info['nome'])
                precos = calcular_preco_plano(servico_selecionado, plano_key)
                
                total_adicionais = st.session_state.form_data.get('num_adicionais', 0) * servico_selecionado['VALOR_ADICIONAL'] * plano_info['meses']
                preco_final_com_adicionais = precos['preco_final'] + total_adicionais

                st.markdown(f"## R$ {(precos['preco_por_mes'] + (st.session_state.form_data.get('num_adicionais', 0) * servico_selecionado['VALOR_ADICIONAL'])):.2f} `/mês`")
                
                if precos['economia'] > 0:
                    st.success(f"Economize R$ {precos['economia']:.2f}!")
                
                st.write(f"Valor do Plano: R$ {precos['preco_final']:.2f}")
                if total_adicionais > 0:
                    st.write(f"Valor Adicionais: R$ {total_adicionais:.2f}")
                st.markdown(f"**Total:** R$ {preco_final_com_adicionais:.2f}")

                if st.button(f"Selecionar {plano_info['nome']}", key=f"btn_{plano_key}", use_container_width=True, type="primary"):
                    st.session_state.form_data['plano_selecionado'] = plano_key
                    next_step()
                    st.rerun()

def step2_dados():
    st.header(f"Etapa 2: Seus Dados (Plano {PLANOS[st.session_state.form_data['plano_selecionado']]['nome']})")
    
    with st.form(key="form_dados_pessoais"):
        st.subheader("Dados Pessoais")
        nome = st.text_input("Nome Completo*", value=st.session_state.form_data.get('NOME', ''))
        cpf = st.text_input("CPF*", value=st.session_state.form_data.get('CPF', ''))
        email = st.text_input("Email*", value=st.session_state.form_data.get('EMAIL', ''))
        telefone = st.text_input("Telefone", value=st.session_state.form_data.get('TELEFONE', ''))

        st.subheader("Endereço")
        cep = st.text_input("CEP*", value=st.session_state.form_data.get('CEP', ''))
        logradouro = st.text_input("Logradouro (Rua, Av.)*", value=st.session_state.form_data.get('LOGRADOURO', ''))
        numero = st.text_input("Número*", value=st.session_state.form_data.get('NUMERO', ''))
        complemento = st.text_input("Complemento (Apto, Bloco, etc.)", value=st.session_state.form_data.get('COMPLEMENTO', ''))
        bairro = st.text_input("Bairro*", value=st.session_state.form_data.get('BAIRRO', ''))
        cidade = st.text_input("Cidade*", value=st.session_state.form_data.get('CIDADE', ''))
        estado = st.text_input("Estado*", value=st.session_state.form_data.get('ESTADO', ''))

        st.subheader("Segurança")
        senha = st.text_input("Crie uma Senha*", type="password")
        confirmar_senha = st.text_input("Confirme sua Senha*", type="password")

        col1, col2 = st.columns(2)
        if col1.form_submit_button("⬅️ Voltar para Planos"):
            prev_step()
            st.rerun()

        if col2.form_submit_button("Avançar para Contrato ➡️", type="primary"):
            campos_obrigatorios = [nome, cpf, email, cep, logradouro, numero, bairro, cidade, estado, senha, confirmar_senha]
            if not all(campos_obrigatorios):
                st.error("❌ Por favor, preencha todos os campos marcados com *.")
            elif senha != confirmar_senha:
                st.error("❌ As senhas não coincidem. Por favor, verifique.")
            else:
                st.session_state.form_data.update({
                    "NOME": nome, "CPF": cpf, "EMAIL": email, "TELEFONE": telefone,
                    "CEP": cep, "LOGRADOURO": logradouro, "NUMERO": numero,
                    "COMPLEMENTO": complemento, "BAIRRO": bairro, "CIDADE": cidade,
                    "ESTADO": estado, "SENHA_HASH": hash_password(senha)
                })
                next_step()
                st.rerun()

def step3_contrato():
    st.header("Etapa 3: Contrato de Adesão")
    st.info("Por favor, baixe o contrato, assine-o (digitalmente ou à mão e escaneie) e faça o upload abaixo.")

    plano_key = st.session_state.form_data['plano_selecionado']
    servico_selecionado = st.session_state.form_data['servico_selecionado']
    
    precos = calcular_preco_plano(servico_selecionado, plano_key)
    num_adicionais = st.session_state.form_data.get('num_adicionais', 0)
    total_adicionais = num_adicionais * servico_selecionado['VALOR_ADICIONAL'] * PLANOS[plano_key]['meses']
    preco_final_com_adicionais = precos['preco_final'] + total_adicionais

    dados_plano_contrato = {
        **PLANOS[plano_key],
        **precos,
        'preco_final_total': preco_final_com_adicionais,
        'num_adicionais': num_adicionais,
        'valor_adicional_unitario': servico_selecionado['VALOR_ADICIONAL'],
        'nomes_adicionais': st.session_state.form_data.get('nomes_adicionais', '')
    }

    pdf_bytes = gerar_contrato_adesao_pdf(st.session_state.form_data, servico_selecionado, dados_plano_contrato, institucional)
    
    st.download_button(
        label="📄 Baixar Contrato de Adesão",
        data=pdf_bytes,
        file_name=f"contrato_adesao_{st.session_state.form_data['NOME'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.divider()

    contrato_assinado = st.file_uploader("Anexe aqui o seu contrato assinado*", type=['pdf', 'jpg', 'png'])
    st.session_state.form_data['contrato_assinado_file'] = contrato_assinado

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar para Dados"):
        prev_step()
        st.rerun()

    if col2.button("Avançar para Finalizar ➡️", type="primary", disabled=(contrato_assinado is None)):
        next_step()
        st.rerun()

def step4_finalizar():
    st.header("Etapa 4: Revisão e Finalização")
    st.success("Tudo pronto! Verifique seus dados e envie sua solicitação.")

    servico_info = st.session_state.form_data['servico_selecionado']
    plano_info = PLANOS[st.session_state.form_data['plano_selecionado']]

    st.write(f"**Serviço Escolhido:** {servico_info['TIPO_SERVICO']} - {servico_info['DESCRICAO_SERVICO']}")
    st.write(f"**Plano de Pagamento:** {plano_info['nome']}")
    if st.session_state.form_data.get('num_adicionais', 0) > 0:
        st.write(f"**Dependentes:** {st.session_state.form_data['num_adicionais']}")
        st.write(f"**Nomes:** {st.session_state.form_data['nomes_adicionais']}")
    st.write(f"**Nome do Titular:** {st.session_state.form_data['NOME']}")
    st.write(f"**Email:** {st.session_state.form_data['EMAIL']}")
    st.write(f"**Contrato Anexado:** {st.session_state.form_data['contrato_assinado_file'].name}")

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar para Contrato"):
        prev_step()
        st.rerun()

    if col2.button("🚀 Enviar Solicitação", type="primary"):
        with st.spinner("Enviando seus dados..."):
            contrato_url = save_uploaded_file(st.session_state.form_data['contrato_assinado_file'], subfolder="contratos")
            
            dados_para_salvar = st.session_state.form_data.copy()
            dados_para_salvar['PLANO_ESCOLHIDO'] = plano_info['nome']
            dados_para_salvar['SERVICO_ESCOLHIDO'] = f"{servico_info['TIPO_SERVICO']} - {servico_info['DESCRICAO_SERVICO']}"
            dados_para_salvar['ADICIONAIS_NOMES'] = dados_para_salvar.get('nomes_adicionais', '')
            dados_para_salvar['CONTRATO_ASSINADO_URL'] = contrato_url
            
            # Limpa dados temporários que não devem ir para o banco
            del dados_para_salvar['plano_selecionado']
            del dados_para_salvar['servico_selecionado']
            del dados_para_salvar['contrato_assinado_file']
            del dados_para_salvar['num_adicionais']
            del dados_para_salvar['nomes_adicionais']

            if salvar_novo_membro(dados_para_salvar):
                st.session_state.step = 5
                st.rerun()
            else:
                st.error("Ocorreu um erro ao salvar seus dados. Tente novamente.")

def step5_sucesso():
    st.balloons()
    st.header("✅ Solicitação enviada com sucesso!")
    st.write("Recebemos seus dados. Sua solicitação está agora pendente de aprovação pela nossa equipe.")
    st.write("Você será notificado por email assim que seu cadastro for ativado.")
    st.page_link("app.py", label="Voltar para a Página Inicial", icon="🏠")

# --- ROTEADOR DE ETAPAS ---
if st.session_state.step == 1:
    step1_selecao()
else:
    if 'servico_selecionado' not in st.session_state.form_data:
        st.warning("Por favor, selecione um serviço para continuar.")
        st.session_state.step = 1
        step1_selecao()
    elif st.session_state.step == 2:
        step2_dados()
    elif st.session_state.step == 3:
        step3_contrato()
    elif st.session_state.step == 4:
        step4_finalizar()
    elif st.session_state.step == 5:
        step5_sucesso()
