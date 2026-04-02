import streamlit as st
import json
import os
import re
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="iPhone & CIA - Diagnóstico Pro", page_icon="📱")

st.markdown("""
    <style>
    [data-testid="stFileUploadDropzone"] > div > div > span { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div > small { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div::before { content: "Arraste o arquivo Panic Full aqui para análise profunda"; font-size: 18px; font-weight: bold; display: block; }
    [data-testid="stFileUploadDropzone"] button::after { content: "Selecionar Log"; font-size: 14px; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; padding: 10px 20px; }
    </style>
""", unsafe_allow_html=True)

st.title(" iPhone & CIA")
st.write("### Sistema Avançado de Diagnóstico 👨‍🔧")
st.write("---")

# --- FUNÇÕES GERAIS ---
def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"🚨 ERRO GRAVE: O arquivo 'padroes.json' está mal formatado! Detalhe técnico: {e}")
            return []
    return []

def carregar_guias():
    if os.path.exists('guias.json'):
        try:
            with open('guias.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"🚨 ERRO: O arquivo 'guias.json' está com problemas! Detalhe: {e}")
            return None
    return None

def registrar_uso(modelo, diagnostico):
    arquivo_historico = 'historico_uso.json'
    historico = []
    if os.path.exists(arquivo_historico):
        try:
            with open(arquivo_historico, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        except: pass
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    historico.append({"Data/Hora": agora, "Aparelho": modelo, "Diagnóstico": diagnostico})
    try:
        with open(arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except: pass

def avanca_passo(novo_passo):
    st.session_state.passo_atual = novo_passo

# --- ESTRUTURA DE ABAS ---
aba1, aba2 = st.tabs(["📄 Leitor de Panic Log", "🧭 Guia Interativo de Bancada"])

# ==========================================
# ABA 1: LEITOR DE PANIC LOG (INALTERADO)
# ==========================================
with aba1:
    try:
        arquivo = st.file_uploader("", key="analise_v28")

        if arquivo is not None:
            nome_arquivo = arquivo.name.lower()
            if not (nome_arquivo.endswith('.ips') or nome_arquivo.endswith('.txt')):
                st.error("⚠️ Formato inválido! Por favor, selecione apenas arquivos de log (.ips ou .txt).")
            else:
                conteudo = arquivo.read().decode("utf-8", errors="ignore")
                padroes = carregar_padroes()
                
                if padroes:
                    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
                    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
                    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
                    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
                    
                    MODELOS = {
                        "iPhone11,2": "iPhone XS", "iPhone11,4": "iPhone XS Max", "iPhone11,6": "iPhone XS Max", "iPhone11,8": "iPhone XR",
                        "iPhone12,1": "iPhone 11", "iPhone12,
