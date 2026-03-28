import streamlit as st
import json
import os

# Configuração da Página
st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

# Estilo Visual (CSS)
st.markdown("""
    <style>
    .titulo-loja { color: #E63946; font-size: 45px; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .apelido { color: #457B9D; font-size: 20px; text-align: center; font-style: italic; margin-top: -10px; margin-bottom: 30px; }
    .resultado-card { padding: 20px; border-radius: 10px; background-color: #f1f1f1; border-left: 5px solid #E63946; }
    </style>
    """, unsafe_markdown=True)

# Cabeçalho Personalizado
st.markdown('<div class="titulo-loja"> iPhone & CIA</div>', unsafe_markdown=True)
st.markdown('<div class="apelido">Sistema de Análise do Chefinho 👨‍🔧</div>', unsafe_markdown=True)

def carregar_padroes():
    if os.path.exists('padroes.json'):
        with open('padroes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_padrao(nome_erro, causa, obs):
    padroes = carregar_padroes()
    padroes[nome_erro] = {"causa": causa, "obs": obs}
    with open('padroes.json', 'w', encoding='utf-8') as f:
        json.dump(padroes, f, indent=4, ensure_ascii=False)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel do Chefinho")
    with st.expander("Cadastrar Novo Erro"):
        novo_erro = st.text_input("Código do Erro")
        nova_causa = st.text_area("Causa Provável")
        nova_obs = st.text_area("Dica Técnica")
        if st.button("💾 Salvar na Memória"):
            salvar_padrao(novo_erro, nova_causa, nova_obs)
            st.success("Aprendido!")

# --- ÁREA DE ANÁLISE ---
arquivo = st.file_uploader("Arraste o log Panic Full aqui", type=["ips", "txt"])

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    encontrado = False
    
    st.subheader("🔍 Resultado da Varredura:")
    
    for erro, info in padroes.items():
        if erro in conteudo:
            st.error(f"### 🚨 {erro} Detectado!")
            st.markdown(f"""
            <div class="resultado-card">
                <strong>🛠 Causa:</strong> {info['causa']}<br><br>
                <strong>💡 Dica do Chefinho:</strong> {info['obs']}
            </div>
            """, unsafe_markdown=True)
            
            # Botão para copiar relatório
            relatorio = f"RELATÓRIO IPHONE & CIA\nErro: {erro}\nCausa: {info['causa']}\nSolução: {info['obs']}"
            st.download_button("📥 Baixar Relatório para o Cliente", relatorio, file_name="diagnostico_iphone.txt")
            encontrado = True
            break
    
    if not encontrado:
        st.warning("Padrão não identificado. O log foi exibido abaixo para análise manual.")
        st.text_area("Texto do Log:", conteudo, height=250)
