import streamlit as st
import json
import os
import re
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="iPhone & CIA - Diagnóstico Pro", page_icon="📱", layout="wide")

# CSS Personalizado
st.markdown("""
    <style>
    [data-testid="stFileUploadDropzone"] > div > div > span { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div > small { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div::before { content: "Arraste o arquivo Panic Full aqui para análise profunda"; font-size: 18px; font-weight: bold; display: block; }
    [data-testid="stFileUploadDropzone"] button::after { content: "Selecionar Log"; font-size: 14px; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; padding: 10px 20px; }
    .guia-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title(" iPhone & CIA")
st.write("### Sistema Avançado de Diagnóstico 👨‍🔧")
st.write("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"🚨 ERRO GRAVE: 'padroes.json' mal formatado! {e}")
    return []

def carregar_guias():
    if os.path.exists('guias.json'):
        try:
            with open('guias.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"🚨 ERRO: 'guias.json' com problemas! {e}")
    return []

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

# --- ESTRUTURA DE ABAS ---
aba1, aba2 = st.tabs(["📄 Leitor de Panic Log", "🧭 Guia Interativo de Bancada"])

# ==========================================
# ABA 1: LEITOR DE PANIC LOG (PRESERVADA)
# ==========================================
with aba1:
    try:
        arquivo = st.file_uploader("", key="analise_v28")

        if arquivo is not None:
            conteudo = arquivo.read().decode("utf-8", errors="ignore")
            padroes = carregar_padroes()
            
            if padroes:
                data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
                data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
                modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
                mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
                
                MODELOS = {
                    "iPhone11,2": "iPhone XS", "iPhone11,4": "iPhone XS Max", "iPhone11,6": "iPhone XS Max", "iPhone11,8": "iPhone XR",
                    "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
                    "iPhone13,1": "iPhone 12 Mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
                    "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
                    "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max"
                }
                modelo_comercial = MODELOS.get(mod_tec, mod_tec)
                area_do_erro = conteudo[:30000].upper()
                
                encontrado = None
                matches_possiveis = []
                for item in padroes:
                    erro_id = item.get("erro", "").upper()
                    if erro_id in area_do_erro:
                        matches_possiveis.append(item)

                st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data:** {data_log}")

                if matches_possiveis:
                    encontrado = matches_possiveis[0]
                    st.error(f"🚨 **Falha Detectada:** {encontrado['erro']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**🔌 Periféricos Suspeitos:**")
                        st.subheader(encontrado['periferico'])
                    with c2:
                        st.write("**🛠 Causa Técnica:**")
                        st.write(encontrado['causa'])
                    
                    st.success(f"**💡 Dica do Chefinho:**\n\n{encontrado['obs'].replace('{modelo}', modelo_comercial)}")
                else:
                    st.warning("⚠️ Padrão não identificado. Envie ao Chefinho para atualização.")

    except Exception as e:
        st.error(f"🚨 Erro no Analisador: {e}")

# ==========================================
# ABA 2: GUIA INTERATIVO DE BANCADA (NOVA)
# ==========================================
with aba2:
    st.subheader("🧭 Assistente de Diagnóstico por Comportamento")
    
    guias = carregar_guias()
    
    if not guias:
        st.warning("Nenhum guia carregado. Verifique o arquivo guias.json")
    else:
        # Gerenciar estado da navegação
        if 'passo_guia' not in st.session_state:
            st.session_state.passo_guia = "inicio"

        # Localizar o nó atual do guia
        no_atual = next((g for g in guias if g['id'] == st.session_state.passo_guia), guias[0])

        st.markdown(f"""<div class="guia-card">
            <h3>{no_atual.get('titulo', 'Análise de Defeito')}</h3>
            <p style="font-size: 18px;">{no_atual.get('pergunta', no_atual.get('descricao', ''))}</p>
        </div>""", unsafe_allow_html=True)

        # Se tiver passos (resultado final)
        if 'passos' in no_atual:
            for p in no_atual['passos']:
                st.write(p)
            if 'referencia' in no_atual:
                st.caption(f"[Link da Solução Completa]({no_atual['referencia']})")
        
        # Gerar botões de opção
        cols = st.columns(len(no_atual.get('opcoes', [])))
        for i, opcao in enumerate(no_atual.get('opcoes', [])):
            if cols[i].button(opcao['texto'], key=f"btn_{opcao['proximo']}_{i}"):
                st.session_state.passo_guia = opcao['proximo']
                st.rerun()

        if st.session_state.passo_guia != "inicio":
            if st.button("⬅️ Voltar ao Início"):
                st.session_state.passo_guia = "inicio"
                st.rerun()
