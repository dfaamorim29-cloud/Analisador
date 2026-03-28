import streamlit as st
import json
import os
import re

# Configuração da Página
st.set_page_config(page_title="iPhone & CIA - Diagnóstico Pro", page_icon="📱")

# Tabela de tradução de modelos
MODELOS = {
    "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
    "iPhone13,1": "iPhone 12 Mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
    "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
    "iPhone17,1": "iPhone 16", "iPhone17,2": "iPhone 16 Pro", "iPhone17,3": "iPhone 16 Pro Max"
}

st.title(" iPhone & CIA")
st.subheader("Sistema de Análise do Chefinho 👨‍🔧")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        with open('padroes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

arquivo = st.file_uploader("Arraste o log Panic Full aqui", type=["ips", "txt"])

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    
    # --- EXTRAÇÃO DE INFORMAÇÕES ---
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)

    # --- EXIBIÇÃO ---
    st.write("---")
    c1, c2 = st.columns(2)
    c1.metric("📱 Modelo", modelo_comercial)
    c2.metric("📅 Data do Log", data_log)
    st.write("---")

    achou_algo = False
    conteudo_maiusculo = conteudo.upper()

    for erro, info in padroes.items():
        # Busca o erro ignorando maiúsculas/minúsculas
        if erro.upper() in conteudo_maiusculo:
            st.error(f"🚨 **FALHA DETECTADA:** {erro}")
            st.warning(f"🔌 **PERIFÉRICO ALVO:** {info.get('periferico', 'Ver dica abaixo')}")
            st.info(f"🛠 **CAUSA:** {info['causa']}")
            st.success(f"💡 **DICA DO CHEFINHO:** {info['obs']}")
            achou_algo = True
            st.divider()
    
    if not achou_algo:
        st.warning("⚠️ Padrão novo detectado! Mande para o Gemini analisar.")
        with st.expander("Ver log completo"):
            st.text(conteudo)
