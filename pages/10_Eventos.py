import streamlit as st
import pandas as pd
from datetime import datetime
from social_utils import display_social_media_links
from auth import get_db_connection

display_social_media_links()
st.set_page_config(page_title="Eventos", layout="wide")

@st.cache_data
def carregar_dados_eventos():
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM eventos", conn)
        df.columns = [x.lower() for x in df.columns]
        df['data_evento'] = pd.to_datetime(df['data_evento'])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar eventos: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

st.title("📅 Calendário de Eventos")
st.write("Fique por dentro de todas as nossas atividades, workshops e confraternizações.")

df_eventos = carregar_dados_eventos()

if df_eventos.empty:
    st.info("Nenhum evento agendado no momento.")
else:
    eventos_agendados = df_eventos[df_eventos['status'] == 'AGENDADO'].sort_values(by="data_evento")
    
    hoje = datetime.now().date()

    proximos_eventos = eventos_agendados[eventos_agendados['data_evento'].dt.date >= hoje]
    eventos_passados = eventos_agendados[eventos_agendados['data_evento'].dt.date < hoje]

    st.header("Próximos Eventos")
    if proximos_eventos.empty:
        st.success("Não há eventos futuros agendados. Fique de olho!")
    else:
        for _, evento in proximos_eventos.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                if pd.notna(evento['imagem_url']) and evento['imagem_url']:
                    col1.image(evento['imagem_url'])
                
                col2.subheader(evento['titulo'])
                col2.write(f"**Data:** {evento['data_evento'].strftime('%d/%m/%Y')} às {evento['hora_evento']}")
                col2.write(f"**Local:** {evento['local']}")
                col2.write(evento['descricao'])

    if not eventos_passados.empty:
        st.divider()
        with st.expander("Ver eventos anteriores"):
            for _, evento in eventos_passados.sort_values(by="data_evento", ascending=False).iterrows():
                 st.write(f"**{evento['data_evento'].strftime('%d/%m/%Y')} - {evento['titulo']}** ({evento['local']})")