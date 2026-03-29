import streamlit as st
import json
import os
import re
import urllib.parse

st.set_page_config(page_title="iPhone & CIA - Diagnóstico Pro", page_icon="📱", layout="wide")

# Interface Profissional em Português
st.markdown("""
    <style>
    [data-testid="stFileUploadDropzone"] > div > div > span { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div > small { display: none; }
    [data-testid="stFileUploadDropzone"] > div > div::before { content: "Arraste o arquivo Panic Full aqui para análise profunda"; font-size: 18px; font-weight: bold; display: block; }
    [data-testid="stFileUploadDropzone"] button::after { content: "Selecionar Log"; font-size: 14px; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title(" iPhone & CIA")
st.write("### Analisador de Hardware de Alta Precisão 👨‍🔧")
st.write("---")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro no arquivo padroes.json: {e}")
            return []
    return []

arquivo = st.file_uploader("", type=["ips", "txt"], key="analise_v13")

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    
    # Extração de Dados
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    
    MODELOS = {
        "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
        "iPhone13,4": "iPhone 12 Pro Max", "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus",
        "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max", "iPhone16,1": "iPhone 15 Pro",
        "iPhone16,2": "iPhone 15 Pro Max", "iPhone17,1": "iPhone 16 Pro", "iPhone17,2": "iPhone 16 Pro Max"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)
    
    # Janela de busca ampliada para 15.000 caracteres
    area_do_erro = conteudo[:15000].upper()
    
    encontrado = None
    matches_possiveis = []

    # Busca exaustiva em todos os padrões
    for item in padroes:
        erro_id = item.get("erro", "").upper()
        modelos_alvo = item.get("modelos", ["TODOS"])
        
        # Verifica se o modelo do log está na lista do erro
        if "TODOS" in modelos_alvo or any(m in modelo_comercial for m in modelos_alvo):
            # Busca por código Hexadecimal ou Decimal
            achou = False
            if erro_id in area_do_erro:
                achou = True
            elif erro_id.startswith("0X"):
                try:
                    dec_val = str(int(erro_id, 16))
                    if dec_val in area_do_erro:
                        achou = True
                except: pass
            
            if achou:
                matches_possiveis.append(item)

    # Priorização: Códigos 0x são mais precisos que textos genéricos
    for m in matches_possiveis:
        if m["erro"].upper().startswith("0X"):
            encontrado = m
            break
    if not encontrado and matches_possiveis:
        encontrado = matches_possiveis[0]

    # Exibição dos Resultados
    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data:** {data_log}")

    if encontrado:
        st.error(f"🚨 **Falha Detectada:** {encontrado['erro']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**🔌 Periféricos Suspeitos:**")
            st.subheader(encontrado['periferico'])
        with col2:
            st.write("**🛠 Causa Técnica:**")
            st.write(encontrado['causa'])
        with col3:
            st.write("**⚠️ Risco do Reparo:**")
            st.info(encontrado.get('risco', 'Médio'))

        if "suspeito_principal" in encontrado:
            st.warning(f"🎯 **Alvo Principal:** {encontrado['suspeito_principal']}")
        
        dica = encontrado['obs'].replace("{modelo}", modelo_comercial)
        st.success(f"**💡 Dica do Chefinho:**\n\n{dica}")
    else:
        st.warning("⚠️ Padrão não identificado. Envie o log para análise manual.")

    # Botão de SOS
    st.write("---")
    email_dest = "dfaamorim29@gmail.com"
    assunto = urllib.parse.quote(f"LOG NÃO IDENTIFICADO - {modelo_comercial}")
    st.markdown(f'<a href="mailto:{email_dest}?subject={assunto}" style="background-color: #007AFF; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">📧 Enviar log para o Chefinho</a>', unsafe_allow_html=True)
