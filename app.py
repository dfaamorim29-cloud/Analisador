import streamlit as st
import json
import os
import re

# Configuração da Página
st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Título e Subtítulo usando comandos nativos (mais seguros)
st.title("iPhone & CIA")
st.write("### Sistema de Análise do Chefinho 👨‍🔧")
st.write("---")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Área de Upload com chave única para evitar repetição
arquivo = st.file_uploader("Arraste o log Panic Full aqui", type=["ips", "txt"], key="analise_atual")

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    conteudo_maiusculo = conteudo.upper()
    padroes = carregar_padroes()
    
    # Extração de Modelo e Data
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    
    # Tabela simples de modelos
    MODELOS = {
        "iPhone12,1": "iPhone 11", "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)

    # Exibe informações do aparelho
    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data do Log:** {data_log}")
    
    achou_algo = False

    # Mostra apenas o resultado do arquivo atual
    for erro, info in padroes.items():
        if erro.upper() in conteudo_maiusculo:
            achou_algo = True
            
            st.error(f"🚨 **Falha Detectada:** {erro}")
            
            # Organização em colunas simples
            c1, c2 = st.columns(2)
            c1.write("**🔌 Periférico Alvo:**")
            c1.write(info.get('periferico', 'N/A'))
            
            c2.write("**🛠 Causa:**")
            c2.write(info.get('causa', 'N/A'))
            
            st.success(f"**💡 Dica do Chefinho:**\n\n{info.get('obs', 'N/A')}")
            st.write("---")
            
    if not achou_algo:
        st.warning("⚠️ Padrão não identificado. Verifique o log abaixo.")
        with st.expander("Ver log completo"):
            st.text(conteudo)
