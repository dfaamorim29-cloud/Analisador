import streamlit as st
import json
import os
import re
import urllib.parse
from datetime import datetime, timedelta, timezone

# Tenta importar a biblioteca de PDF
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

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

# --- FUNÇÃO GERADORA DE RECIBO EM PDF ---
def gerar_pdf_recibo(cliente, cpf, modelo, servico, garantia, pagamento, valor):
    pdf = FPDF()
    pdf.add_page()
    
    def texto_limpo(texto):
        if not texto: return ""
        # Converte caracteres especiais para evitar erros no PDF
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    # Cabeçalho da Empresa
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, texto_limpo("iPhone & Cia - Assistência Técnica em Goiânia"), ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, texto_limpo("CNPJ: 31.042.442/0001-24 | Telefone/WhatsApp: (62) 99289-7531"), ln=True, align='C')
    pdf.ln(10)

    # Título do Documento
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, texto_limpo("RECIBO DE PRESTAÇÃO DE SERVIÇOS"), ln=True, align='C')
    pdf.ln(5)

    # Texto principal do Recibo
    pdf.set_font("Arial", '', 12)
    texto_recibo = f"Recebemos de {cliente}, inscrito(a) sob o CPF {cpf}, a importância de R$ {valor} referente ao pagamento do serviço detalhado abaixo."
    pdf.multi_cell(0, 8, texto_limpo(texto_recibo))
    pdf.ln(5)

    # Detalhes Técnicos
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, texto_limpo("Detalhes do Aparelho e Serviço:"), ln=True)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, texto_limpo(f"- Aparelho: {modelo}"), ln=True)
    pdf.cell(0, 8, texto_limpo(f"- Serviço Executado: {servico}"), ln=True)
    pdf.cell(0, 8, texto_limpo(f"- Forma de Pagamento: {pagamento}"), ln=True)
    pdf.cell(0, 8, texto_limpo(f"- Garantia do Serviço: {garantia}"), ln=True)
    pdf.ln(15)

    # Data e Local (Goiânia - GO)
    fuso_br = timezone(timedelta(hours=-3))
    data_atual = datetime.now(fuso_br).strftime("%d/%m/%Y")
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, texto_limpo(f"Goiânia - GO, {data_atual}"), ln=True, align='R')
    pdf.ln(25)

    # Assinatura
    pdf.cell(0, 8, "_____________________________________________________", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, texto_limpo("iPhone & Cia - Assistência Técnica"), ln=True, align='C')
    
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, texto_limpo("Nota: A garantia cobre apenas o serviço executado. Não cobre mau uso, quedas ou contato com líquidos."), ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# BARRA LATERAL (ADMINISTRAÇÃO DO CHEFINHO)
# ==========================================
with st.sidebar:
    st.write("### ⚙️ Painel de Controle")
    st.write("Área restrita da gerência.")
    
    # 🔒 Senha
    senha = st.text_input("Senha de Acesso:", type="password", key="senha_admin")
    
    if senha == "admin123":
        st.success("Acesso Liberado!")
        
        # MENU DE NAVEGAÇÃO DO ADMIN
        menu_admin = st.radio("Escolha a Ferramenta:", ["📊 Histórico de Logs", "🧾 Gerador de Recibos"])
        st.write("---")
        
        if menu_admin == "📊 Histórico de Logs":
            st.write("**Histórico de Diagnósticos**")
            if os.path.exists('historico_uso.json'):
                try:
                    with open('historico_uso.json', 'r', encoding='utf-8') as f:
                        historico = json.load(f)
                        if historico:
                            st.metric(label="Total de Análises Realizadas", value=len(historico))
                            st.dataframe(historico[::-1], use_container_width=True)
                        else:
                            st.info("Nenhum registro encontrado.")
                except:
                    st.error("Erro ao ler o histórico.")
            else:
                st.info("O arquivo de histórico ainda não foi criado.")
                
        elif menu_admin == "🧾 Gerador de Recibos":
            st.write("**Emissão de Recibo Rápida**")
            
            if not HAS_FPDF:
                st.error("A biblioteca 'fpdf' não está instalada. O recibo não pode ser gerado.")
            else:
                with st.form("form_recibo"):
                    rec_cliente = st.text_input("Nome do Cliente:")
                    rec_cpf = st.text_input("CPF do Cliente:")
                    rec_modelo = st.text_input("Modelo do Aparelho (Ex: iPhone 11 Pro):")
                    rec_servico = st.text_input("Serviço Executado (Ex: Troca de Tela, Reparo em Placa):")
                    rec_valor = st.text_input("Valor do Serviço (Ex: 450,00):")
                    
                    rec_pagamento = st.selectbox("Forma de Pagamento:", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
                    rec_garantia = st.selectbox("Garantia:", ["90 Dias (Padrão)", "30 Dias", "Sem Garantia (Aparelho Oxidado)", "Especial (Descrita no Serviço)"])
                    
                    btn_gerar_recibo = st.form_submit_button("Gerar Recibo PDF", type="primary")
                    
                if btn_gerar_recibo:
                    if rec_cliente and rec_valor and rec_servico:
                        pdf_recibo_bytes = gerar_pdf_recibo(
                            rec_cliente, rec_cpf, rec_modelo, rec_servico, rec_garantia, rec_pagamento, rec_valor
                        )
                        st.success("✅ Recibo gerado com sucesso!")
                        st.download_button(
                            label="📥 Baixar Recibo PDF",
                            data=pdf_recibo_bytes,
                            file_name=f"Recibo_iPhone_e_Cia_{rec_cliente.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.warning("Preencha ao menos Nome, Serviço e Valor para gerar.")

# ==========================================
# CORPO PRINCIPAL DO SISTEMA
# ==========================================
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
        
    fuso_br = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")
    
    historico.append({"Data/Hora": agora, "Aparelho": modelo, "Diagnóstico": diagnostico})
    try:
        with open(arquivo_historico, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)
    except: pass

def gerar_pdf_laudo(modelo, data_log, falha, periferico, causa, risco, alvo, dica):
    pdf = FPDF()
    pdf.add_page()
    
    def texto_limpo(texto):
        if not texto: return ""
        return str(texto).encode('latin-1', 'ignore').decode('latin-1')

    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 10, "LAUDO TECNICO - IPHONE & CIA", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, texto_limpo(f"Aparelho: {modelo}"), ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, texto_limpo(f"Data do Log (Diagnostico): {data_log}"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(255, 0, 0)
    pdf.cell(0, 10, texto_limpo(f"FALHA DETECTADA: {falha}"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Perifericos Suspeitos / Modulos:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, texto_limpo(periferico))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Causa Tecnica do Reinicio:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, texto_limpo(causa))
    pdf.ln(2)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, texto_limpo(f"Nivel de Risco do Reparo: {risco}"), ln=True)
    if alvo:
        pdf.cell(0, 8, texto_limpo(f"Alvo Principal: {alvo}"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Conclusao / Parecer Tecnico:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, texto_limpo(dica))
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, "Este laudo foi gerado automaticamente pelo Sistema Avancado de Diagnostico iPhone & CIA.", ln=True, align='C')

    return pdf.output(dest='S').encode('latin-1')

# --- ESTRUTURA DE ABAS ---
aba1, aba2 = st.tabs(["📄 Leitor de Panic Log", "🧭 Guia Interativo de Bancada"])

# ==========================================
# ABA 1: LEITOR DE PANIC LOG
# ==========================================
with aba1:
    try:
        if 'uploader_key' not in st.session_state:
            st.session_state.uploader_key = 0

        arquivo = st.file_uploader("", key=f"analise_v28_{st.session_state.uploader_key}")

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
                            
                        risco = encontrado.get('risco', 'Médio')
                        st.info(f"**⚠️ Nível do Reparo:** {risco}")
                        
                        if "ALTO" in risco.upper():
                            st.error("🛑 **ALERTA DE BANCADA:** Reparo de placa avançado. É OBRIGATÓRIO informar ao cliente que o procedimento envolve calor na placa e existe risco real do aparelho apagar em definitivo durante o processo.")

                        alvo_principal = encontrado.get("suspeito_principal", "")
                        if alvo_principal:
                            st.warning(f"🎯 **Alvo Principal:** {alvo_principal}")
                        
                        dica = encontrado['obs'].replace("{modelo}", modelo_comercial)
                        st.success(f"**💡 Dica do Chefinho:**\n\n{dica}")
                    else:
                        st.warning("⚠️ Padrão não identificado. Por favor, envie este log para o Chefinho para que ele possa fazer a correção do código e adicionar este novo defeito ao sistema.")
                        
                    if "log_registrado" not in st.session_state or st.session_state.log_registrado != arquivo.name:
                        resultado_texto = encontrado['erro'] if encontrado else "Não Identificado"
                        registrar_uso(modelo_comercial, resultado_texto)
                        st.session_state.log_registrado = arquivo.name

                    st.write("---")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("🔄 Analisar Novo Log", type="primary", use_container_width=True):
                            st.session_state.uploader_key += 1
                            st.rerun()
                            
                    with col_btn2:
                        if encontrado:
                            if HAS_FPDF:
                                pdf_bytes = gerar_pdf_laudo(
                                    modelo_comercial, data_log, encontrado['erro'], 
                                    encontrado['periferico'], encontrado['causa'], 
                                    risco, alvo_principal, dica
                                )
                                st.download_button(
                                    label="📄 Baixar Laudo em PDF",
                                    data=pdf_bytes,
                                    file_name=f"Laudo_{modelo_comercial.replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.warning("⚠️ Instale a biblioteca fpdf (pip install fpdf) para gerar laudos.")
                        
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
        if 'passo_guia' not in st.session_state:
            st.session_state.passo_guia = "inicio"
            
        if 'modelo_selecionado' not in st.session_state:
            st.session_state.modelo_selecionado = ""

        no_atual = next((g for g in guias if g['id'] == st.session_state.passo_guia), guias[0])

        st.markdown('<div class="guia-card">', unsafe_allow_html=True)
        
        col_titulo, col_btn = st.columns([3, 1])
        
        with col_titulo:
            if st.session_state.passo_guia != "inicio" and st.session_state.modelo_selecionado:
                st.markdown(f"<span style='color: #666; font-size: 15px; font-weight: bold;'>📱 Aparelho Selecionado: {st.session_state.modelo_selecionado}</span>", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='color: #007AFF; margin-top: 5px;'>{no_atual.get('titulo', 'Nova Consulta')}</h3>", unsafe_allow_html=True)
            
            if 'pergunta' in no_atual or 'descricao' in no_atual:
                st.markdown(f"<p style='font-size: 18px;'>{no_atual.get('pergunta', no_atual.get('descricao', ''))}</p>", unsafe_allow_html=True)
                
        with col_btn:
            if st.session_state.passo_guia != "inicio":
                if st.button("🏠 Voltar ao Início", type="primary", use_container_width=True):
                    st.session_state.passo_guia = "inicio"
                    st.session_state.modelo_selecionado = ""
                    st.rerun()

        if 'passos' in no_atual:
            for p in no_atual['passos']:
                st.markdown(p)
                
            texto_completo = " ".join(no_atual['passos']).lower()
            palavras_de_risco = ['reballing', 'cpu', 'nand', 'interposer', 'bga', 'solda', 'reflow']
            
            if any(palavra in texto_completo for palavra in palavras_de_risco):
                st.write("") 
                st.error("🛑 **ALERTA DE BANCADA:** Este diagnóstico indica um reparo a nível de componente que exige aquecimento da placa. **É OBRIGATÓRIO alertar o cliente sobre os riscos envolvidos**, incluindo a possibilidade de o aparelho desligar permanentemente (risco de morte) devido ao estresse térmico antes de aprovar o orçamento.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")

        opcoes = no_atual.get('opcoes', [])
        
        cols = st.columns(len(opcoes)) if len(opcoes) > 0 else []
        
        for i, opcao in enumerate(opcoes):
            if cols[i].button(opcao['texto'], key=f"btn_{opcao['proximo']}_{i}", use_container_width=True):
                if st.session_state.passo_guia == "inicio":
                    st.session_state.modelo_selecionado = opcao['texto']
                
                st.session_state.passo_guia = opcao['proximo']
                st.rerun()
