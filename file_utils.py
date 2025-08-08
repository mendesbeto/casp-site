import pandas as pd
from io import BytesIO
import os
from datetime import datetime

def dataframe_to_excel_bytes(df):
    """Converte um pandas DataFrame para um arquivo Excel em memória (bytes)."""
    output = BytesIO()
    # Usar o ExcelWriter para poder especificar o nome da aba
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    processed_data = output.getvalue()
    return processed_data

def save_uploaded_file(uploaded_file, subfolder="convenios"):
    """Salva um arquivo enviado em uma subpasta de 'uploads' e retorna o caminho."""
    upload_dir = os.path.join("uploads", subfolder)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename, extension = os.path.splitext(uploaded_file.name)
    unique_filename = f"{filename}_{timestamp}{extension}"
    
    filepath = os.path.join(upload_dir, unique_filename)
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath.replace("\\", "/")

def get_convenios_df():
    """Lê o arquivo de convênios e o retorna como um DataFrame."""
    return pd.read_csv("data/convenios.csv")

def save_convenios_df(df):
    """Salva o DataFrame de convênios no arquivo CSV."""
    df.to_csv("data/convenios.csv", index=False)

def get_beneficios_df():
    """Lê o arquivo de benefícios e o retorna como um DataFrame."""
    return pd.read_csv("data/beneficios.csv")

def save_beneficios_df(df):
    """Salva o DataFrame de benefícios no arquivo CSV."""
    df.to_csv("data/beneficios.csv", index=False)

def get_usuarios_df():
    """Lê o arquivo de usuários e o retorna como um DataFrame."""
    return pd.read_csv("data/usuarios.csv")

def save_usuarios_df(df):
    """Salva o DataFrame de usuários no arquivo CSV."""
    df.to_csv("data/usuarios.csv", index=False)

def get_log_atividades():
    """Lê o arquivo de log de atividades e o retorna como um DataFrame."""
    return pd.read_csv("data/log_atividades.csv")

def get_noticias_df():
    """Lê o arquivo de notícias e o retorna como um DataFrame."""
    return pd.read_csv("data/noticias.csv")

def save_noticias_df(df):
    """Salva o DataFrame de notícias no arquivo CSV."""
    df.to_csv("data/noticias.csv", index=False)

def get_eventos_df():
    """Lê o arquivo de eventos e o retorna como um DataFrame."""
    return pd.read_csv("data/eventos.csv")

def save_eventos_df(df):
    """Salva o DataFrame de eventos no arquivo CSV."""
    df.to_csv("data/eventos.csv", index=False)