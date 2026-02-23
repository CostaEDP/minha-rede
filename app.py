import streamlit as st
import pandas as pd
import requests
from math import radians, cos, sin, asin, sqrt

# Configuração da Página - Nome que aparece na aba do navegador
st.set_page_config(page_title="Localizador PTs", layout="wide")

# Função para calcular distância
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

# --- SIDEBAR ---
st.sidebar.title("Configurações")
m_lat = st.sidebar.number_input("Minha Latitude", value=39.5000, format="%.6f")
m_lon = st.sidebar.number_input("Minha Longitude", value=-8.0000, format="%.6f")

# --- CORPO DA APP ---
st.title("📍 Localizador Postos de Transformação")
st.markdown("Pesquisa em tempo real na base de dados nacional da E-REDES.")

# Caixa de texto para os códigos
entrada = st.text_area("Insira os códigos dos PTs (separados por vírgula ou espaço):", 
                       placeholder="Exemplo: 1824D2010700, 1824D2011100")

if entrada:
    # Limpa a entrada e cria lista de códigos
    cods = [c.strip().upper() for c in entrada.replace(',', ' ').split()]
    
    encontrados = []
    
    for c in cods:
        # Chama a API da E-REDES para cada código
        url = f"https://e-redes.opendatasoft.com/api/records/1.0/search/?dataset=postos-transformacao-distribuicao&q={c}"
        try:
            response = requests.get(url).json()
            if response.get('records'):
                for rec in response['records']:
                    fields = rec['fields']
                    geo = rec['geometry']['coordinates']
                    lat, lon = geo[1], geo[0]
                    dist = calcular_distancia(m_lat, m_lon, lat, lon)
                    
                    encontrados.append({
                        'id': fields.get('cod_instalacao'),
                        'concelho': fields.get('con_name'),
                        'dist': dist, 'lat': lat, 'lon': lon
                    })
        except:
            st.error(f"Erro na ligação para o código {c}")

    if encontrados:
        # Ordena por distância (mais perto primeiro)
        rota = sorted(encontrados, key=lambda x: x['dist'])
        
        # Mapa dos pontos encontrados
        st.map(pd.DataFrame(rota))

        st.subheader("📋 Lista de Postos (Ordenada por Proximidade)")
        for i, pt in enumerate(rota, 1):
            with st.expander(f"Paragem {i}: {pt['id']} - {pt['concelho']} ({pt['dist']:.2f} km)"):
                # Coordenadas prontas a copiar
                st.code(f"{pt['lat']}, {pt['lon']}")
                
                c1, c2 = st.columns(2)
                # Link para Google Maps
                c1.link_button("📍 Iniciar GPS", f"https://www.google.com/maps/search/?api=1&query={pt['lat']},{pt['lon']}")
                # Link para GeoCloud
                c2.link_button("🔍 Ver no GeoCloud", f"https://geocloud.e-redes.pt/geoviewer/index.html?center={pt['lat']},{pt['lon']}&level=18")
    else:
        st.warning("Nenhum posto encontrado com esses códigos.")
else:
    st.info("Aguardando introdução de códigos para gerar roteiro.")
