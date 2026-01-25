import streamlit as st
import json

st.set_page_config(page_title="E-REDES SOS", page_icon="⚡")
st.title("⚡ Localizador de PTs")

# Tenta abrir o ficheiro de dados
try:
    with open('postos-transformacao-distribuicao.geojson', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    busca = st.text_input("Escreve o Concelho (ex: Sertã) ou o código do PT:")

    if busca:
        encontrados = 0
        for item in dados['features']:
            info = item['properties']
            gps = item['geometry']['coordinates']
            
            # Se o que escreveste estiver no nome ou no código
            if busca.upper() in str(info.get('con_name', '')).upper() or busca.upper() in str(info.get('cod_instalacao', '')).upper():
                encontrados += 1
                col1, col2 = st.columns([3, 1])
                col1.write(f"**PT: {info.get('cod_instalacao')}** ({info.get('con_name')})")
                
                # Link para o Google Maps (Latitude é gps[1], Longitude é gps[0])
                link_gps = f"https://www.google.com/maps/search/?api=1&query={gps[1]},{gps[0]}"
                col2.link_button("📍 GPS", link_gps)
                st.divider()
                
                if encontrados > 40: # Limite para não encravar o telemóvel
                    st.warning("Muitos resultados. Tenta ser mais específico.")
                    break
except Exception as e:
    st.error("Ficheiro de dados não encontrado. Verifica o nome no GitHub.")