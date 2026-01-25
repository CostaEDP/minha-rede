import streamlit as st
import json
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="E-REDES Rota Eficiente", page_icon="⚡")

# Função para calcular distância real entre ti e o PT
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371 # Raio da Terra em km
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

st.title("⚡ Rota Otimizada de Inspeção")

# 1. Carregar os dados
try:
    with open('postos-transformacao-distribuicao.geojson', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # 2. Onde estás agora? (Podes copiar do Google Maps e colar aqui)
    st.sidebar.header("📍 Minha Localização Atual")
    minha_lat = st.sidebar.number_input("Tua Latitude", value=39.8475, format="%.6f")
    minha_lon = st.sidebar.number_input("Tua Longitude", value=-8.1000, format="%.6f")

    # 3. Pesquisa os PTs (podes escrever vários códigos separados por vírgula ou apenas a zona)
    busca = st.text_input("Escreve o nome da zona (ex: Sertã) para ver os PTs mais próximos:")

    if busca:
        lista_provisoria = []
        for item in dados['features']:
            p = item['properties']
            g = item['geometry']
            
            if busca.upper() in str(p.get('con_name', '')).upper() or busca.upper() in str(p.get('cod_instalacao', '')).upper():
                lon, lat = g['coordinates']
                dist = calcular_distancia(minha_lat, minha_lon, lat, lon)
                lista_provisoria.append({
                    'id': p.get('cod_instalacao'),
                    'dist': dist,
                    'lat': lat, 'lon': lon
                })
        
        # ORDENAÇÃO MÁGICA: Do mais perto para o mais longe
        rota_ordenada = sorted(lista_provisoria, key=lambda x: x['dist'])

        st.subheader("📋 Ordem Sugerida de Visita:")
        st.info("O primeiro da lista é o que está mais perto de ti agora.")

        for i, pt in enumerate(rota_ordenada[:10], 1): # Mostra os 10 mais próximos
            with st.expander(f"Paragem {i}: PT {pt['id']} (a {pt['dist']:.2f} km)"):
                st.write(f"Este é o {i}º ponto mais próximo.")
                url = f"https://www.google.com/maps/dir/?api=1&origin={minha_lat},{minha_lon}&destination={pt['lat']},{pt['lon']}&travelmode=driving"
                st.link_button(f"Iniciar Navegação para PT {pt['id']}", url)

except Exception as e:
    st.error("Erro ao carregar ficheiro. Verifica se o nome no GitHub está correto.")
