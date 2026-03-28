import streamlit as st
import json
import os

# Configuração simples e robusta
st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Título direto e profissional
st.title(" iPhone & CIA")
st.subheader("Sistema de Análise do Chefinho 👨‍🔧")

# Função para carregar os padrões
def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# --- ÁREA DE UPLOAD ---
st.write("### 📤 Subir Arquivo de Log")
arquivo = st.file_uploader("Escolha o arquivo .ips ou .txt", type=["ips", "txt"])

if arquivo:
    try:
        # Lê o arquivo e ignora letras maiúsculas/minúsculas
        conteudo = arquivo.read().decode("utf-8")
        conteudo_maiusculo = conteudo.upper()
        padroes = carregar_padroes()
        achou_algo = False

        st.write("---")
        st.write("### 📋 Resultado da Análise:")

        for erro, info in padroes.items():
            # Procura cada erro do seu banco de dados dentro do log
            if erro.upper() in conteudo_maiusculo:
                st.error(f"🚨 **FALHA DETECTADA:** {erro}")
                st.info(f"🛠 **CAUSA:** {info['causa']}")
                st.success(f"💡 **DICA DO CHEFINHO:** {info['obs']}")
                achou_algo = True
                st.write("---")
        
        if not achou_algo:
            st.warning("⚠️ Padrão não identificado automaticamente.")
            st.write("Chefinho, esse erro deve ser novo! Copie o começo do log e mande aqui para eu te ajudar.")
            with st.expander("Clique aqui para ver o texto do log"):
                st.text(conteudo)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
