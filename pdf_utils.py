from fpdf import FPDF
from datetime import datetime
import pandas as pd

class PDF(FPDF):
    def __init__(self, dados_institucionais, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dados_institucionais = dados_institucionais

    def header(self):
        # Adiciona o logo
        self.image('assets/logo.png', 10, 8, 25)
        self.set_font('Arial', 'B', 15)
        # Move para a direita para não sobrepor o logo
        self.cell(80)
        # Título
        self.cell(30, 10, self.dados_institucionais['TITULO_SITE'], 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_recibo_pdf(dados_cobranca, dados_usuario, dados_institucionais):
    pdf = PDF(dados_institucionais)
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Recibo de Pagamento', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recebemos de:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, f"Nome: {dados_usuario['NOME']}\nCPF: {dados_usuario['CPF']}", border=0, align='L')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Referente a:', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    valor_formatado = f"R$ {dados_cobranca['VALOR']:.2f}".replace('.', ',')
    data_pagamento = pd.to_datetime(dados_cobranca['DATA_PAGAMENTO']).strftime('%d/%m/%Y') if pd.notna(dados_cobranca['DATA_PAGAMENTO']) else "N/A"
    pdf.multi_cell(0, 7, f"Serviço Contratado: {dados_cobranca['SERVICO_CONTRATADO']}\nValor: {valor_formatado}\nData do Pagamento: {data_pagamento}", border=0, align='L')
    pdf.ln(20)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Emitido em: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(10)
    pdf.cell(0, 10, '______________________________________', 0, 1, 'C')
    pdf.cell(0, 5, f"CNPJ: {dados_institucionais['CNPJ_CPF']}", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

def gerar_contrato_adesao_pdf(dados_usuario, dados_servico, dados_plano, dados_institucionais):
    pdf = PDF(dados_institucionais)
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Contrato de Adesão de Associado', 0, 1, 'C')
    pdf.ln(10)

    # --- DADOS DA ASSOCIAÇÃO (CONTRATADA) --- 
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'CONTRATADA:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, 
        f"Razão Social: {dados_institucionais['TITULO_SITE']}\n"
        f"CNPJ: {dados_institucionais['CNPJ_CPF']}\n"
        f"Endereço: {dados_institucionais['ENDERECO']}", 
        border=0, align='L')
    pdf.ln(5)

    # --- DADOS DO ASSOCIADO (CONTRATANTE) --- 
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'CONTRATANTE:', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, 
        f"Nome: {dados_usuario['NOME']}\n"
        f"CPF: {dados_usuario['CPF']}\n"
        f"Email: {dados_usuario['EMAIL']}\n"
        f"Endereço: {dados_usuario['LOGRADOURO']}, {dados_usuario['NUMERO']} - {dados_usuario['BAIRRO']}, {dados_usuario['CIDADE']}/{dados_usuario['ESTADO']}",
        border=0, align='L')
    pdf.ln(5)

    # --- OBJETO DO CONTRATO --- 
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. OBJETO DO CONTRATO', 0, 1)
    pdf.set_font('Arial', '', 12)
    texto_objeto = (
        "O presente contrato tem por objeto a associação do CONTRATANTE ao quadro de membros da CONTRATADA, "
        "garantindo-lhe o direito de usufruir dos benefícios, convênios e serviços oferecidos, "
        f"especificamente o serviço '{dados_servico['TIPO_SERVICO']}', conforme as normas e regulamentos da associação."
    )
    pdf.multi_cell(0, 7, texto_objeto, border=0, align='J')
    pdf.ln(5)

    # --- SERVIÇO E PLANO ESCOLHIDO --- 
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. SERVIÇO, PLANO E VALORES', 0, 1)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 7, f"Serviço Contratado: {dados_servico['TIPO_SERVICO']}", 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 7, f"Descrição: {dados_servico['DESCRICAO_SERVICO']}", border=0, align='J')
    pdf.ln(3)
    
    valor_plano_formatado = f"R$ {dados_plano['preco_final_total']:.2f}".replace('.', ',')
    texto_plano = (
        f"O CONTRATANTE adere ao plano de pagamento '{dados_plano['nome']}', com duração de {dados_plano['meses']} mes(es). "
        f"O valor total para o período é de {valor_plano_formatado}. "
        "O pagamento deverá ser efetuado após a aprovação do cadastro."
    )
    pdf.multi_cell(0, 7, texto_plano, border=0, align='J')
    pdf.ln(3)

    if dados_plano.get('num_adicionais', 0) > 0:
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, f"Dependentes Incluídos: {dados_plano['num_adicionais']}", 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 7, f"Nomes: {dados_plano['nomes_adicionais']}", border=0, align='J')
        pdf.ln(5)

    # --- ASSINATURAS --- 
    pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.ln(20)
    
    pdf.cell(0, 10, '______________________________________', 0, 1, 'C')
    pdf.cell(0, 5, f"{dados_usuario['NOME']}", 0, 1, 'C')
    pdf.cell(0, 5, "(CONTRATANTE)", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.cell(0, 10, '______________________________________', 0, 1, 'C')
    pdf.cell(0, 5, f"{dados_institucionais['TITULO_SITE']}", 0, 1, 'C')
    pdf.cell(0, 5, "(CONTRATADA)", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')