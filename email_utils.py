import streamlit as st
import smtplib
from email.message import EmailMessage
import pandas as pd

def send_recovery_email(recipient_email: str, token: str, email_config: dict):
    """
    Envia um email de recuperação de senha para o usuário.
    Agora recebe as credenciais e a URL base como um dicionário.
    """
    try:
        # Carrega as credenciais e a URL do dicionário
        sender_email = email_config["email_address"]
        sender_password = email_config["email_password"]
        base_url = email_config["base_url"]

        # Cria a mensagem do email
        msg = EmailMessage()
        msg['Subject'] = "Recuperação de Senha - Associação de Benefícios"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Monta o link de recuperação
        recovery_link = f"{base_url}/Recuperar_Senha?token={token}"

        # Corpo do email em HTML para melhor formatação
        html_content = f"""
        <html>
        <body>
            <h2>Recuperação de Senha</h2>
            <p>Olá,</p>
            <p>Você solicitou a recuperação de sua senha. Clique no link abaixo para redefinir sua senha:</p>
            <p style="font-size: 16px; font-weight: bold;"><a href="{recovery_link}">{recovery_link}</a></p>
            <p>Este link é válido por 15 minutos.</p>
            <p>Se você não solicitou esta recuperação, por favor, ignore este email.</p>
            <br>
            <p>Atenciosamente,</p>
            <p>Equipe da Associação</p>
        </body>
        </html>
        """
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        # Verifica se o erro é de autenticação SMTP
        if isinstance(e, smtplib.SMTPAuthenticationError):
            st.error("Falha na autenticação com o servidor de email. Verifique as credenciais de email no arquivo de segredos (secrets.toml).")
            st.error("Para contas do Gmail, é recomendável usar uma 'Senha de App'.")
        else:
            st.error(f"Erro ao enviar email: {e}")
        return False

def send_due_date_reminder_email(recipient_email: str, charge_details: dict, email_creds: dict):
    """
    Envia um email de lembrete de vencimento de cobrança.
    Agora recebe as credenciais como um dicionário.
    """
    try:
        sender_email = email_creds["email_address"]
        sender_password = email_creds["email_password"]

        msg = EmailMessage()
        msg['Subject'] = f"Lembrete de Vencimento: {charge_details['DESCRICAO']}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        nome_membro = charge_details.get('NOME', 'Membro').split(' ')[0]
        valor_formatado = f"R$ {charge_details['VALOR']:.2f}".replace('.', ',')
        # A data pode vir como string ou objeto date, então garantimos a conversão
        data_vencimento_formatada = pd.to_datetime(charge_details['DATA_VENCIMENTO']).strftime('%d/%m/%Y') 

        html_content = f"""
        <html>
        <body>
            <h2>Lembrete de Vencimento</h2>
            <p>Olá, {nome_membro},</p>
            <p>Este é um lembrete amigável sobre a sua cobrança que está próxima do vencimento:</p>
            <ul>
                <li><strong>Descrição:</strong> {charge_details['DESCRICAO']}</li>
                <li><strong>Valor:</strong> {valor_formatado}</li>
                <li><strong>Data de Vencimento:</strong> {data_vencimento_formatada}</li>
            </ul>
            <p>Por favor, realize o pagamento para evitar inconvenientes. Você pode ver mais detalhes em sua área de membro.</p>
            <br>
            <p>Atenciosamente,</p>
            <p>Equipe da Associação</p>
        </body>
        </html>
        """
        msg.add_alternative(html_content, subtype='html')

                
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        # Verifica se o erro é de autenticação SMTP
        if isinstance(e, smtplib.SMTPAuthenticationError):
            st.error("Falha na autenticação com o servidor de email. Verifique as credenciais de email no arquivo de segredos (secrets.toml).")
            st.error("Para contas do Gmail, é recomendável usar uma 'Senha de App'.")
        else:
            st.error(f"Erro ao enviar email: {e}")
        return False

def send_due_date_reminder_email(recipient_email: str, charge_details: dict, email_creds: dict):
    """
    Envia um email de lembrete de vencimento de cobrança.
    Agora recebe as credenciais como um dicionário.
    """
    try:
        sender_email = email_creds["email_address"]
        sender_password = email_creds["email_password"]

        msg = EmailMessage()
        msg['Subject'] = f"Lembrete de Vencimento: {charge_details['DESCRICAO']}"
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        nome_membro = charge_details.get('NOME', 'Membro').split(' ')[0]
        valor_formatado = f"R$ {charge_details['VALOR']:.2f}".replace('.', ',')
        # A data pode vir como string ou objeto date, então garantimos a conversão
        data_vencimento_formatada = pd.to_datetime(charge_details['DATA_VENCIMENTO']).strftime('%d/%m/%Y') 

        html_content = f"""
        <html>
        <body>
            <h2>Lembrete de Vencimento</h2>
            <p>Olá, {nome_membro},</p>
            <p>Este é um lembrete amigável sobre a sua cobrança que está próxima do vencimento:</p>
            <ul>
                <li><strong>Descrição:</strong> {charge_details['DESCRICAO']}</li>
                <li><strong>Valor:</strong> {valor_formatado}</li>
                <li><strong>Data de Vencimento:</strong> {data_vencimento_formatada}</li>
            </ul>
            <p>Por favor, realize o pagamento para evitar inconvenientes. Você pode ver mais detalhes em sua área de membro.</p>
            <br>
            <p>Atenciosamente,</p>
            <p>Equipe da Associação</p>
        </body>
        </html>
        """
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        # Usamos print para que o erro apareça no console/log da tarefa agendada
        print(f"ERRO: Falha ao enviar email de lembrete para {recipient_email}. Detalhes: {e}")
        return False

def send_renewal_reminder_email(recipient_email: str, member_details: dict, email_creds: dict):
    """
    Envia um email de lembrete de renovação de anuidade.
    Agora recebe as credenciais como um dicionário.
    """
    try:
        sender_email = email_creds["email_address"]
        sender_password = email_creds["email_password"]

        msg = EmailMessage()
        msg['Subject'] = "Lembrete de Aniversário de Associação!"
        msg['From'] = sender_email
        msg['To'] = recipient_email

        html_content = f"""
        <html>
        <body>
            <h2>Feliz Aniversário de Associação, {member_details['NOME'].split(' ')[0]}!</h2>
            <p>Olá,</p>
            <p>Gostaríamos de parabenizá-lo pelo seu aniversário em nossa associação! Agradecemos por fazer parte da nossa comunidade.</p>
            <p>Este é um lembrete amigável para a renovação da sua anuidade, que ajuda a manter todos os benefícios que você já conhece.</p>
            <p>Para qualquer dúvida, entre em contato conosco.</p>
            <br>
            <p>Atenciosamente,</p>
            <p>Equipe da Associação</p>
        </body>
        </html>
        """
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar email de renovação: {e}")
        return False

