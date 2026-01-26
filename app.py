import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="Agenda de Campo", page_icon="📅")

st.title("📅 Agenda de Trabalho com GPS")

# 1. Configuração da Jornada
st.sidebar.header("⚙️ Configurações")
hora_inicio = st.sidebar.time_input("Hora de Início", value=datetime.strptime("08:00", "%H:%M"))
tempo_em_cada = st.sidebar.number_input("Tempo em cada local (min)", value=30)
tempo_viagem_padrao = st.sidebar.number_input("Tempo médio de viagem (min)", value=15)

# 2. Entrada de Dados (Onde planeias o teu dia)
st.subheader("📝 Planear Dia")
instrucoes = """Formato: Nome ou Código | Coordenadas ou Morada | Notas
Exemplo:
PT Sertã 01 | 39.8475,-8.1000 | Levar escada e verificar fusível
Poste 44 | Rua da Igreja, Sertã | Pintar numeração
"""
entrada = st.text_area("Cria a tua lista (um por linha):", value="", height=200, placeholder=instrucoes)

if entrada:
    trabalhos = entrada.strip().split('\n')
    hora_atual = datetime.combine(datetime.today(), hora_inicio)
    
    st.divider()
    st.subheader("🚀 Roteiro do Dia")
    
    for i, linha in enumerate(trabalhos):
        if '|' in linha:
            partes = linha.split('|')
            nome = partes[0].strip()
            local = partes[1].strip()
            nota = partes[2].strip() if len(partes) > 2 else "Sem notas."
            
            # Cálculos de tempo
            chegada = hora_atual + timedelta(minutes=tempo_viagem_padrao if i > 0 else 0)
            saida = chegada + timedelta(minutes=tempo_em_cada)
            
            # Cartão de Trabalho
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {i+1}. {nome}")
                    st.caption(f"📍 {local}")
                    st.info(f"🗒️ **Nota:** {nota}")
                
                with col2:
                    st.write(f"⌚ **Chegada**\n{chegada.strftime('%H:%M')}")
                    st.write(f"⌚ **Saída**\n{saida.strftime('%H:%M')}")
                    
                    # Botão de GPS
                    # Se for coordenada (tem virgula e números), funciona direto. 
                    # Se for morada, o Google Maps também reconhece.
                    url_maps = f"https://www.google.com/maps/search/?api=1&query={local.replace(' ', '+')}"
                    st.link_button("📍 Ir agora", url_maps)
            
            hora_atual = saida

    st.success(f"🏁 Hora prevista de fim de serviço: {hora_atual.strftime('%H:%M')}")
else:
    st.info("Escreve os teus trabalhos na caixa acima para gerares a agenda do dia.")
