import streamlit as st
import pandas as pd
import requests
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="Localizador Postos de Transformação", layout="wide")

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

# --- CONFIGURAÇÃO ---
st.sidebar.title("Configurações Nacionais")
m_lat = st.sidebar.number_input("Tua Latitude", value=39.5000, format="%.6f")
m_lon = st.sidebar.number_input("Tua Longitude", value=-8.0000, format="%.6f")

    st.title("Localizador Postos de Transformação")
    st.info("A pesquisar em tempo real na base de dados oficial de Portugal.")

    entrada = st.text_area("Insere os códigos dos PTs (ex: 1824D2010700):")

    if entrada:
        cods = [c.strip().upper() for c in entrada.replace(',', ' ').split()]
        
        encontrados = []
        
        for c in cods:
            # PESQUISA DIRETA NA API DA E-REDES
            url = f"https://e-redes.opendatasoft.com/api/records/1.0/search/?dataset=postos-transformacao-distribuicao&q={c}"
            try:
                response = requests.get(url).json()
                if response['records']:
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
                st.error(f"Erro ao ligar à base de dados para o PT {c}")

        if encontrados:
            rota = sorted(encontrados, key=lambda x: x['dist'])
            st.map(pd.DataFrame(rota))

            for i, pt in enumerate(rota, 1):
                with st.expander(f"📍 {i}: {pt['id']} - {pt['concelho']} ({pt['dist']:.2f} km)"):
                    st.code(f"{pt['lat']}, {pt['lon']}")
                    col1, col2 = st.columns(2)
                    col1.link_button("📍 GPS", f"https://www.google.com/maps/search/?api=1&query={pt['lat']},{pt['lon']}")
                    col2.link_button("🔍 GeoCloud", f"https://geocloud.e-redes.pt/geoviewer/index.html?center={pt['lat']},{pt['lon']}&level=18")
        else:
            st.warning("Nenhum código encontrado em Portugal.")
else:
    if senha: st.error("Senha incorreta")
    st.info("Introduza a senha para aceder ao mapa nacional.")





