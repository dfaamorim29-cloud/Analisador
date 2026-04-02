import streamlit as st
import json
import os
import re
import urllib.parse
from datetime import datetime

# Layout centralizado garantido
st.set_page_config(page_title="iPhone & CIA - Diagnóstico Pro", page_icon="📱", layout="centered")

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
            return []
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
# ABA 1: LEITOR DE PANIC LOG
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
                        "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
                        "iPhone13,1": "iPhone 12 Mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
                        "iPhone14,4": "iPhone 13 Mini", "iPhone14,5": "iPhone 13", "iPhone14,2": "iPhone 13 Pro", "iPhone14,3": "iPhone 13 Pro Max",
                        "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
                        "iPhone15,4": "iPhone 15 Plus", "iPhone15,5": "iPhone 15", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
                        "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max", "iPhone17,3": "iPhone 16", "iPhone17,4": "iPhone 16 Plus"
                    }
                    modelo_comercial = MODELOS.get(mod_tec, mod_tec)
                    
                    area_do_erro = conteudo[:30000].upper()
                    
                    if "LAST LOADED KEXT" in area_do_erro:
                        area_do_erro = area_do_erro.split("LAST LOADED KEXT")[0]
                    elif "LOADED KEXTS" in area_do_erro:
                        area_do_erro = area_do_erro.split("LOADED KEXTS")[0]
                    
                    encontrado = None
                    matches_possiveis = []

                    for item in padroes:
                        erro_id = item.get("erro", "").upper()
                        modelos_alvo = item.get("modelos", ["TODOS"])
                        
                        if "TODOS" in modelos_alvo or any(m in modelo_comercial for m in modelos_alvo):
                            achou = False
                            if not erro_id.startswith("0X") and erro_id in area_do_erro:
                                achou = True
                            elif erro_id.startswith("0X"):
                                if re.search(r'\b' + erro_id + r'\b', area_do_erro):
                                    achou = True
                                else:
                                    try:
                                        dec_num = int(erro_id, 16)
                                        if dec_num > 10000: 
                                            if re.search(r'\b' + str(dec_num) + r'\b', area_do_erro):
                                                achou = True
                                    except: pass
                            if achou:
                                matches_possiveis.append(item)

                    if matches_possiveis:
                        matches_possiveis.sort(key=lambda x: x.get("peso", 99))
                        encontrado = matches_possiveis[0]

                    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data:** {data_log}")

                    if encontrado:
                        st.error(f"🚨 **Falha Detectada:** {encontrado['erro']}")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("**🔌 Periféricos Suspeitos:**")
                            st.subheader(encontrado['periferico'])
                        with c2:
                            st.write("**🛠 Causa Técnica:**")
                            st.write(encontrado['causa'])
                            
                        st.info(f"**⚠️ Risco do Reparo:** {encontrado.get('risco', 'Médio')}")

                        if "suspeito_principal" in encontrado:
                            st.warning(f"🎯 **Alvo Principal:** {encontrado['suspeito_principal']}")
                        
                        dica = encontrado['obs'].replace("{modelo}", modelo_comercial)
                        st.success(f"**💡 Dica do Chefinho:**\n\n{dica}")
                    else:
                        st.warning("⚠️ Padrão não identificado. Por favor, envie este log para o Chefinho para que ele possa fazer a correção do código e adicionar este novo defeito ao sistema.")
                        
                    if "log_registrado" not in st.session_state or st.session_state.log_registrado != arquivo.name:
                        resultado_texto = encontrado['erro'] if encontrado else "Não Identificado"
                        registrar_uso(modelo_comercial, resultado_texto)
                        st.session_state.log_registrado = arquivo.name

                    st.write("---")
                    email_dest = "dfaamorim29@gmail.com"
                    assunto = urllib.parse.quote(f"LOG PARA CORREÇÃO DE CÓDIGO - {modelo_comercial}")
                    corpo = urllib.parse.quote(f"Chefinho, o site não conseguiu analisar este arquivo do {modelo_comercial} e não encontrou o padrão. Segue em anexo para você analisar e fazer a correção do código-fonte!\n\n(Lembre-se de anexar o arquivo .ips ou .txt)")
                    st.markdown(f'<a href="mailto:{email_dest}?subject={assunto}&body={corpo}" style="background-color: #007AFF; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">📧 Enviar log para correção do código</a>', unsafe_allow_html=True)

    except Exception as erro_geral:
        st.error(f"🚨 Ocorreu um erro inesperado no sistema: {erro_geral}")

# ==========================================
# ABA 2: GUIA INTERATIVO DE BANCADA
# ==========================================
with aba2:
    st.subheader("🧭 Assistente de Diagnóstico de Placa")
    
    guias = carregar_guias()
    
    if not guias:
        st.warning("Nenhum guia carregado. Verifique o arquivo guias.json")
    else:
        # Gerenciar estado da navegação e modelo
        if 'passo_guia' not in st.session_state:
            st.session_state.passo_guia = "inicio"
            
        if 'modelo_selecionado' not in st.session_state:
            st.session_state.modelo_selecionado = ""

        # Localizar o nó atual do guia
        no_atual = next((g for g in guias if g['id'] == st.session_state.passo_guia), guias[0])

        # Estrutura do cabeçalho com colunas para o botão "Voltar ao Início"
        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        col_titulo, col_btn = st.columns([3, 1])
        
        with col_titulo:
            # Mostra o modelo selecionado (se não estiver no início)
            if st.session_state.passo_guia != "inicio" and st.session_state.modelo_selecionado:
                st.markdown(f"<span style='color: #666; font-size: 15px; font-weight: bold;'>📱 Aparelho Selecionado: {st.session_state.modelo_selecionado}</span>", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='color: #007AFF; margin-top: 5px;'>{no_atual.get('titulo', 'Nova Consulta')}</h3>", unsafe_allow_html=True)
            
            if 'pergunta' in no_atual or 'descricao' in no_atual:
                st.markdown(f"<p style='font-size: 18px;'>{no_atual.get('pergunta', no_atual.get('descricao', ''))}</p>", unsafe_allow_html=True)
                
        with col_btn:
            # Botão de Voltar ao Início azul (type="primary") só aparece se não estiver no início
            if st.session_state.passo_guia != "inicio":
                if st.button("🏠 Voltar ao Início", type="primary", use_container_width=True):
                    st.session_state.passo_guia = "inicio"
                    st.session_state.modelo_selecionado = ""
                    st.rerun()

        # Se tiver passos (resultado final)
        if 'passos' in no_atual:
            for p in no_atual['passos']:
                st.markdown(p)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")

        # Gerar botões de navegação
        opcoes = no_atual.get('opcoes', [])
        
        # Cria colunas para os botões ficarem lado a lado
        cols = st.columns(len(opcoes)) if len(opcoes) > 0 else []
        
        for i, opcao in enumerate(opcoes):
            if cols[i].button(opcao['texto'], key=f"btn_{opcao['proximo']}_{i}", use_container_width=True):
                # Se estiver no início, salva qual aparelho foi clicado
                if st.session_state.passo_guia == "inicio":
                    st.session_state.modelo_selecionado = opcao['texto']
                
                st.session_state.passo_guia = opcao['proximo']
                st.rerun()
