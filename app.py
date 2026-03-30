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
    historico.append({
        "Data/Hora": agora,
        "Aparelho": modelo,
        "Diagnóstico": diagnostico
    })
    
    try:
        with open(arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except: pass

arquivo = st.file_uploader("", key="analise_v25")

if arquivo:
    nome_arquivo = arquivo.name.lower()
    if not (nome_arquivo.endswith('.ips') or nome_arquivo.endswith('.txt')):
        st.error("⚠️ Formato inválido! Por favor, selecione apenas arquivos de log (.ips ou .txt).")
    else:
        conteudo = arquivo.read().decode("utf-8", errors="ignore")
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
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**🔌 Periféricos Suspeitos:**")
                st.subheader(encontrado['periferico'])
            with col2:
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

st.write("")
st.write("")
st.write("")
with st.expander("🔒"):
    senha = st.text_input("Chave de Acesso:", type="password")
    if senha == "iphoneecia":
        st.success("Acesso Liberado!")
        st.write("### 📊 Histórico de Utilização")
        
        if os.path.exists('historico_uso.json'):
            try:
                with open('historico_uso.json', 'r', encoding='utf-8') as f:
                    dados_historico = json.load(f)
                
                if dados_historico:
                    st.metric("Total de Análises Realizadas", len(dados_historico))
                    st.dataframe(dados_historico, use_container_width=True)
                else:
                    st.info("Nenhuma análise registada ainda.")
            except:
                st.error("Erro ao ler o histórico.")
        else:
            st.info("O ficheiro de histórico ainda não foi criado (faça a primeira análise).")
