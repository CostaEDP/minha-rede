import streamlit as st
import json
from math import radians, cos, sin, asin, sqrt

st.set_page_config(page_title="E-REDES Planeador GPS")

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dLat, dLon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dLat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dLon/2)**2
    return R * 2 * asin(sqrt(a))

st.title(" Planeador Rota Sertâ")
st.markdown("Insira os códigos para criar o roteiro e obter as coordenadas GPS.")

try:
    # Carregar o ficheiro (garante que o nome coincide com o que tens no GitHub)
    with open('postos-transformacao-distribuicao.geojson', 'r', encoding='utf-8') as f:
        dados = json.load(f)

    # Localização de partida
    st.sidebar.header("📍 Ponto de Partida")
    m_lat = st.sidebar.number_input("Tua Latitude Atual", value=39.8475, format="%.6f")
    m_lon = st.sidebar.number_input("Tua Longitude Atual", value=-8.1000, format="%.6f")

    # CAIXA DE PESQUISA MÚLTIPLA
    entrada = st.text_area("Colar aqui COD do PT"):", 
                           placeholder="Exemplo: 1824D2010700, 1824D2011100")

    if entrada:
        # Limpar a entrada para criar uma lista de códigos
        lista_procurar = entrada.replace(',', ' ').split()
        lista_procurar = [c.strip().upper() for c in lista_procurar]

        pts_encontrados = []
        for feature in dados['features']:
            p = feature['properties']
            g = feature['geometry']
            
            # Tenta encontrar o código em várias colunas possíveis (PT, Apoio ou OCR)
            cod_id = str(p.get('cod_instalacao') or p.get('cod_apoio') or p.get('cod_equipamento') or '').upper()
            
            if cod_id in lista_procurar:
                lon, lat = g['coordinates']
                dist = calcular_distancia(m_lat, m_lon, lat, lon)
                pts_encontrados.append({
                    'id': cod_id,
                    'dist': dist,
                    'lat': lat, 
                    'lon': lon,
                    'concelho': p.get('con_name', 'N/A')
                })

        if pts_encontrados:
            # Ordenar do mais próximo para o mais distante
            rota_eficiente = sorted(pts_encontrados, key=lambda x: x['dist'])

            st.success(f"✅ Encontrados {len(pts_encontrados)} pontos. Roteiro gerado!")
            
            # Mapa visual
            st.map(pts_encontrados)

            st.subheader("📋 Ordem de Visita e Dados GPS")
            for i, pt in enumerate(rota_eficiente, 1):
                with st.expander(f"📍 PARAGEM {i}: Código {pt['id']}"):
                    st.write(f"**Distância:** {pt['dist']:.2f} km")
                    
                    # --- AQUI ESTÃO AS COORDENADAS PARA COPIAR ---
                    st.code(f"{pt['lat']}, {pt['lon']}", language=None)
                    st.caption("Podes copiar a coordenada acima ↑")
                    
                    st.write(f"**Localidade:** {pt['concelho']}")
                    
                    # Botão de Navegação
                    url = f"https://www.google.com/maps/search/?api=1&query={pt['lat']},{pt['lon']}"
                    st.link_button(f"Abrir GPS para {pt['id']}", url)
        else:
            st.warning("Nenhum código foi encontrado. Verifica se os códigos estão corretos ou se o ficheiro GeoJSON está atualizado.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")




