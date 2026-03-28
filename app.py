import streamlit as st
import json
import os
import re

# Configuração da Página
st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Tabela de tradução de modelos
MODELOS = {
    "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
    "iPhone13,1": "iPhone 12 Mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
    "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
    "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max"
}

# Cabeçalho da Loja
st.markdown("<h1 style='text-align: center; color: #E63946;'> iPhone & CIA</h1>", unsafe_markdown=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Sistema de Análise do Chefinho 👨‍🔧</p>", unsafe_markdown=True)
st.write("---")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        with open('padroes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Área de Upload - Ao subir um novo, o Streamlit limpa o anterior automaticamente
arquivo = st.file_uploader("Arraste o log Panic Full aqui", type=["ips", "txt"], key="analisador_unico")

if arquivo:
    # Lendo o arquivo atual
    conteudo = arquivo.read().decode("utf-8")
    conteudo_maiusculo = conteudo.upper()
    padroes = carregar_padroes()
    
    # Extração básica de Modelo e Data
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)

    # Exibe informações do aparelho analisado agora
    st.info(f"**Aparelho:** {modelo_comercial}  |  **Data do Log:** {data_log}")
    
    achou_algo = False

    # Analisando o conteúdo
    for erro, info in padroes.items():
        if erro.upper() in conteudo_maiusculo:
            achou_algo = True
            
            # Layout dos 4 itens solicitados pelo Chefinho
            st.markdown(f"### 🚨 Falha Detectada: `{erro}`")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**🔌 Periférico Alvo:**\n{info.get('periferico', 'N/A')}")
            with col2:
                st.markdown(f"**🛠 Causa:**\n{info.get('causa', 'N/A')}")
            
            st.success(f"**💡 Dica do Chefinho:**\n{info.get('obs', 'N/A')}")
            st.write("---")
            
    if not achou_algo:
        st.warning("⚠️ O Chefinho ainda não cadastrou esse padrão de erro.")
        with st.expander("Ver texto do log para estudo"):
            st.text(conteudo)
