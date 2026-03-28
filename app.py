import streamlit as st
import json
import os

# Configuração da Página
st.set_page_config(page_title="Analisador de Logs - iPhone & CIA", page_icon="📱")

# Função para carregar os padrões salvos
def carregar_padroes():
    if os.path.exists('padroes.json'):
        with open('padroes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Função para salvar novos padrões
def salvar_padrao(nome_erro, causa, obs):
    padroes = carregar_padroes()
    padroes[nome_erro] = {"causa": causa, "obs": obs}
    with open('padroes.json', 'w', encoding='utf-8') as f:
        json.dump(padroes, f, indent=4, ensure_ascii=False)

st.title("🔍 Analisador de Logs IPS")
st.write("Arraste o arquivo .ips abaixo para identificar a falha.")

# --- BARRA LATERAL PARA NOVOS PADRÕES ---
with st.sidebar:
    st.header("⚙️ Adicionar Novo Padrão")
    novo_erro = st.text_input("Nome do Erro (Ex: AOP PANIC)")
    nova_causa = st.text_area("Causa Provável")
    nova_obs = st.text_area("Observações Técnicas")
    if st.button("Salvar Padrão"):
        salvar_padrao(novo_erro, nova_causa, nova_obs)
        st.success("Padrão adicionado com sucesso!")

# --- ÁREA DE UPLOAD ---
arquivo = st.file_uploader("Escolha o arquivo Panic Full", type=["ips", "txt"])

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    encontrado = False

    st.subheader("📋 Resultado da Análise:")
    
    for erro, info in padroes.items():
        if erro in conteudo:
            st.error(f"**Falha Detectada:** {erro}")
            st.warning(f"**Causa:** {info['causa']}")
            st.info(f"**Dica Técnica:** {info['obs']}")
            encontrado = True
            break
    
    if not encontrado:
        st.success("Nenhum padrão conhecido encontrado. Verifique manualmente o log.")
        st.text_area("Conteúdo do Log para inspeção:", conteudo, height=200)
