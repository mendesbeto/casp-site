import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Eventos", layout="wide")

@st.cache_data
def carregar_dados_eventos():
    try:
        df = pd.read_csv('data/eventos.csv')
        # Convertendo a coluna de data para o formato datetime para comparação
        df['DATA_EVENTO'] = pd.to_datetime(df['DATA_EVENTO'])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

st.title("📅 Calendário de Eventos")
st.write("Fique por dentro de todas as nossas atividades, workshops e confraternizações.")

df_eventos = carregar_dados_eventos()

if df_eventos.empty:
    st.info("Nenhum evento agendado no momento.")
else:
    eventos_agendados = df_eventos[df_eventos['STATUS'] == 'AGENDADO'].sort_values(by="DATA_EVENTO")
    
    hoje = datetime.now().date()

    proximos_eventos = eventos_agendados[eventos_agendados['DATA_EVENTO'].dt.date >= hoje]
    eventos_passados = eventos_agendados[eventos_agendados['DATA_EVENTO'].dt.date < hoje]

    st.header("Próximos Eventos")
    if proximos_eventos.empty:
        st.success("Não há eventos futuros agendados. Fique de olho!")
    else:
        for _, evento in proximos_eventos.iterrows():
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                if pd.notna(evento['IMAGEM_URL']) and evento['IMAGEM_URL']:
                    col1.image(evento['IMAGEM_URL'])
                
                col2.subheader(evento['TITULO'])
                col2.write(f"**Data:** {evento['DATA_EVENTO'].strftime('%d/%m/%Y')} às {evento['HORA_EVENTO']}")
                col2.write(f"**Local:** {evento['LOCAL']}")
                col2.write(evento['DESCRICAO'])

    if not eventos_passados.empty:
        st.divider()
        with st.expander("Ver eventos anteriores"):
            for _, evento in eventos_passados.sort_values(by="DATA_EVENTO", ascending=False).iterrows():
                 st.write(f"**{evento['DATA_EVENTO'].strftime('%d/%m/%Y')} - {evento['TITULO']}** ({evento['LOCAL']})")