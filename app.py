import streamlit as st
import json
import os
import re
import urllib.parse

st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Interface Traduzida
st.markdown("""
    <style>
    [data-testid="stFileUploadDropzone"] > div > div > span { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div > small { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div::before { content: "Arraste e solte o arquivo do log aqui"; font-size: 16px; font-weight: 500; display: block; }
    [data-testid="stFileUploadDropzone"] > div > div::after { content: "Arquivos suportados: .ips ou .txt"; font-size: 14px; color: #808495; display: block; }
    [data-testid="stFileUploadDropzone"] button { font-size: 0px; }
    [data-testid="stFileUploadDropzone"] button::after { content: "Procurar Arquivo"; font-size: 14px; font-weight: 400; }
    </style>
""", unsafe_allow_html=True)

st.title(" iPhone & CIA")
st.write("### Sistema de Análise do Chefinho 👨‍🔧")
st.write("---")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

arquivo = st.file_uploader("Selecione o relatório de erro:", type=["ips", "txt"], key="analise_v11")

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    
    # Extração de Modelo e Data
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    
    MODELOS = {
        "iPhone11,2": "iPhone XS", "iPhone12,1": "iPhone 11", "iPhone13,4": "iPhone 12 Pro Max",
        "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", 
        "iPhone15,3": "iPhone 14 Pro Max", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)
    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data do Log:** {data_log}")

    # Varredura completa para não perder os decimais (786432, 4194304, etc)
    conteudo_full = conteudo.upper()
    encontrado = None
    
    # BUSCA DE PRIORIDADE
    # 1º: Procura códigos hexadecimais (0X...) e suas versões decimais
    for item in padroes:
        erro_id = item.get("erro", "")
        if erro_id.lower().startswith("0x"):
            dec_val = str(int(erro_id, 16))
            if erro_id.upper() in conteudo_full or re.search(r'\b' + dec_val + r'\b', conteudo_full):
                if "TODOS" in item["modelos"] or any(m in modelo_comercial for m in item["modelos"]):
                    encontrado = item
                    break
    
    # 2º: Se não achou código, procura por nomes de sensores ou falhas de texto
    if not encontrado:
        for item in padroes:
            erro_id = item.get("erro", "")
            if not erro_id.lower().startswith("0x") and erro_id.upper() in conteudo_full:
                if "TODOS" in item["modelos"] or any(m in modelo_comercial for m in item["modelos"]):
                    encontrado = item
                    break

    if encontrado:
        st.error(f"🚨 **Falha Detectada:** {encontrado['erro']}")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**🔌 Periféricos Suspeitos:**")
            st.subheader(encontrado['periferico'])
        with c2:
            st.write("**🛠 Causa:**")
            st.write(encontrado['causa'])
            
        if "suspeito_principal" in encontrado:
            st.warning(f"🎯 **Alvo Principal:** {encontrado['suspeito_principal']}")
        
        dica = encontrado['obs'].replace("{modelo}", modelo_comercial)
        st.success(f"**💡 Dica do Chefinho:**\n\n{dica}")
    else:
        st.warning("⚠️ Padrão não identificado.")

    # Botão de SOS para o seu e-mail
    st.write("---")
    email_link = f"mailto:dfaamorim29@gmail.com?subject=Analise%20Incorreta%20-{modelo_comercial}&body=Anexe%20o%20arquivo%20aqui."
    st.markdown(f'<a href="{email_link}" target="_blank" style="background-color: #007AFF; color: white; padding: 10px; border-radius: 5px; text-decoration: none;">📧 Enviar log para o Chefinho</a>', unsafe_allow_html=True)
