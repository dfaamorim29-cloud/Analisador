import streamlit as st
import json
import os
import re
import urllib.parse

st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Interface Traduzida para Português
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

arquivo = st.file_uploader("Selecione o relatório de erro:", type=["ips", "txt"], key="analise_v12")

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    
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
        "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)
    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data do Log:** {data_log}")

    conteudo_full = conteudo.upper()
    encontrado = None
    
    # 1ª PRIORIDADE: Códigos Numéricos (0x...) e suas conversões decimais
    for item in padroes:
        erro_id = item.get("erro", "")
        if erro_id.lower().startswith("0x"):
            dec_val = str(int(erro_id, 16))
            # Busca o Hexadecimal ou o Decimal no texto
            if erro_id.upper() in conteudo_full or re.search(r'\b' + dec_val + r'\b', conteudo_full):
                if "TODOS" in item["modelos"] or any(m in modelo_comercial for m in item["modelos"]):
                    encontrado = item
                    break # Se achou o número, para tudo e foca nele!

    # 2ª PRIORIDADE: Erros de Texto (Watchdog, RootDomain, etc)
    if not encontrado:
        for item in padroes:
            erro_id = item.get("erro", "")
            # Evita falsos positivos com nomes genéricos de sensores
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

    # Botão de Envio de Log para o Chefinho
    st.write("---")
    st.markdown("### 📩 Ajude a melhorar o sistema!")
    email_dest = "dfaamorim29@gmail.com"
    assunto = urllib.parse.quote(f"Novo Log - {modelo_comercial}")
    corpo = urllib.parse.quote(f"Chefinho, o site não identificou corretamente este log do {modelo_comercial}. Segue em anexo para análise.")
    st.markdown(f'<a href="mailto:{email_dest}?subject={assunto}&body={corpo}" target="_blank" style="background-color: #007AFF; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">📧 Enviar log para o Chefinho</a>', unsafe_allow_html=True)
