import streamlit as st
import json
import os
import re
import urllib.parse

st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Lógica de CSS para traduzir a caixa de Upload (Drag and Drop / Browse Files)
st.markdown("""
    <style>
    /* Oculta os textos em inglês originais */
    [data-testid="stFileUploadDropzone"] > div > div > span { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div > small { display: none; }
    
    /* Cria o novo texto principal em Português */
    [data-testid="stFileUploadDropzone"] > div > div::before {
        content: "Arraste e solte o arquivo do log aqui";
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 5px;
        display: block;
    }
    
    /* Cria o texto de limite de ficheiro em Português */
    [data-testid="stFileUploadDropzone"] > div > div::after {
        content: "Arquivos suportados: .ips ou .txt (Máx: 200MB)";
        font-size: 14px;
        color: #808495;
        display: block;
    }
    
    /* Tradução do botão "Browse files" */
    [data-testid="stFileUploadDropzone"] button {
        font-size: 0px; 
    }
    [data-testid="stFileUploadDropzone"] button::after {
        content: "Procurar Arquivo";
        font-size: 14px; 
        font-weight: 400;
    }
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

arquivo = st.file_uploader("Selecione o relatório de erro (Panic Full):", type=["ips", "txt"], key="analise_v10")

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
        "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max",
        "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max", "iPhone17,3": "iPhone 16", "iPhone17,4": "iPhone 16 Plus",
        "iPhone18,1": "iPhone 17 Pro", "iPhone18,2": "iPhone 17 Pro Max"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)
    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data do Log:** {data_log}")

    area_do_erro = conteudo[:6000].upper()
    encontrado = None
    
    for item in padroes:
        erro_original = item.get("erro", "")
        erro_upper = erro_original.upper()
        modelos_alvo = item.get("modelos", ["TODOS"])
        
        achou = False
        
        if erro_upper in area_do_erro:
            achou = True
        
        elif erro_original.lower().startswith("0x"):
            try:
                erro_dec = str(int(erro_original, 16)) 
                if re.search(r'\b' + erro_dec + r'\b', area_do_erro):
                    achou = True
            except:
                pass
                
        if achou:
            if "TODOS" in modelos_alvo or any(m in modelo_comercial for m in modelos_alvo):
                if erro_original.lower().startswith("0x"):
                    encontrado = item
                    break 
                elif not encontrado:
                    encontrado = item 

    if encontrado:
        dica_formatada = encontrado.get('obs', 'N/A').replace("{modelo}", modelo_comercial)
        
        st.error(f"🚨 **Falha Detectada:** {encontrado['erro']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**🔌 Periféricos Suspeitos:**")
            st.subheader(encontrado.get('periferico', 'N/A'))
        with c2:
            st.write("**🛠 Causa:**")
            st.write(encontrado.get('causa', 'N/A'))
            
        if "suspeito_principal" in encontrado:
            st.warning(f"🎯 **Alvo Principal:** {encontrado['suspeito_principal']}")
        
        st.success(f"**💡 Dica do Chefinho:**\n\n{dica_formatada}")
    else:
        st.warning("⚠️ Padrão não identificado para este modelo.")
        
    # --- NOVA SESSÃO: BOTÃO DE E-MAIL PARA O CHEFINHO ---
    st.write("---")
    st.markdown("### 📩 Ajude a melhorar o sistema!")
    st.write("O site não identificou o erro ou indicou a peça errada? Envie o arquivo para o Chefinho analisar e atualizar o banco de dados.")
    
    # Preparando os dados do e-mail
    email_destino = "dfaamorim29@gmail.com"
    assunto = f"Novo Log para Analise - {modelo_comercial}"
    corpo_mensagem = f"Chefinho, o site não conseguiu analisar corretamente este log do {modelo_comercial}. Estou enviando em anexo para você dar uma olhada e adicionar ao padroes.json!\n\n(Lembre-se de anexar o arquivo .ips ou .txt neste e-mail antes de enviar)"
    
    # Codificando o texto para não dar erro no navegador
    assunto_codificado = urllib.parse.quote(assunto)
    corpo_codificado = urllib.parse.quote(corpo_mensagem)
    
    link_email = f"mailto:{email_destino}?subject={assunto_codificado}&body={corpo_codificado}"
    
    # Criando um botão estilizado
    st.markdown(
        f"""
        <a href="{link_email}" target="_blank" style="
            display: inline-block;
            padding: 10px 20px;
            background-color: #007AFF;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            margin-top: 10px;
        ">
        📧 Enviar log para o Chefinho
        </a>
        <br><small style="color: gray;">Lembre-se de anexar o arquivo do log no e-mail que vai abrir!</small>
        """, 
        unsafe_allow_html=True
    )
