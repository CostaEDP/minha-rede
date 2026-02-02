import streamlit as st
import json
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="E-REDES Planeador", page_icon="⚡")

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

st.title("Rota de Inspeção PTs")
st.markdown("Insira os códigos dos PTs para criar o roteiro mais eficiente.")

try:
    with open('postos-transformacao-distribuicao.geojson', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Localização de partida
    st.sidebar.header("📍 Ponto de Partida")
    m_lat = st.sidebar.number_input("Tua Latitude", value=39.8475, format="%.6f")
    m_lon = st.sidebar.number_input("Tua Longitude", value=-8.1000, format="%.6f")

    # CAIXA DE PESQUISA MÚLTIPLA
    entrada = st.text_area("Cole aqui os códigos dos PTs (separados por vírgula, espaço ou linha):", 
                           placeholder="Exemplo: 1824D2010700, 1824D2011100, 1824D2014600")

    if entrada:
        # Limpar a entrada para criar uma lista de códigos
        lista_procurar = entrada.replace(',', ' ').split()
        lista_procurar = [c.strip().upper() for c in lista_procurar]

        pts_encontrados = []
        for feature in dados['features']:
            p = feature['properties']
            g = feature['geometry']
            cod_pt = str(p.get('cod_instalacao', '')).upper()
            
            if cod_pt in lista_procurar:
                lon, lat = g['coordinates']
                dist = calcular_distancia(m_lat, m_lon, lat, lon)
                pts_encontrados.append({
                    'id': cod_pt,
                    'dist': dist,
                    'lat': lat, 'lon': lon,
                    'concelho': p.get('con_name')
                })

        if pts_encontrados:
            # ORDENAR: A mágica acontece aqui - organiza do mais próximo para o mais distante
            rota_eficiente = sorted(pts_encontrados, key=lambda x: x['dist'])

            st.success(f"✅ Roteiro gerado para {len(pts_encontrados)} postos!")
            
            # Mostrar a rota no mapa (opcional)
            st.map(pts_encontrados)

            for i, pt in enumerate(rota_eficiente, 1):
                with st.expander(f"📍 PARAGEM {i}: PT {pt['id']}"):
                    st.write(f"**Localidade:** {pt['concelho']}")
                    st.write(f"**Distância de onde estás:** {pt['dist']:.2f} km")
                    
                    # Link para o Google Maps
                    url = f"https://www.google.com/maps/dir/?api=1&origin={m_lat},{m_lon}&destination={pt['lat']},{pt['lon']}&travelmode=driving"
                    st.link_button(f"Abrir Navegação para Paragem {i}", url)
                    
                    # Atualiza a posição "m_lat" e "m_lon" para o próximo cálculo se quisesses rota encadeada
                    # Mas para inspeção simples, a distância da origem atual costuma ser o melhor guia.
        else:
            st.warning("Nenhum desses códigos foi encontrado no ficheiro da Sertã.")

except Exception as e:
    st.error(f"Erro: {e}")

