import streamlit as st
import json
import os
import re

# Configuração da Página
st.set_page_config(page_title="iPhone & CIA - Diagnóstico", page_icon="📱")

st.title("iPhone & CIA")
st.write("### Sistema de Análise do Chefinho 👨‍🔧")
st.write("---")

def carregar_padroes():
    if os.path.exists('padroes.json'):
        try:
            with open('padroes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

arquivo = st.file_uploader("Arraste o log Panic Full aqui", type=["ips", "txt"], key="analise_precisa")

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    padroes = carregar_padroes()
    
    # 1. Extração do Modelo e Data
    data_match = re.search(r'"date"\s*:\s*"([^"]+)"', conteudo)
    data_log = data_match.group(1)[:19] if data_match else "Desconhecida"
    modelo_match = re.search(r'"product"\s*:\s*"([^"]+)"', conteudo)
    mod_tec = modelo_match.group(1) if modelo_match else "Desconhecido"
    
    MODELOS = {
        "iPhone12,1": "iPhone 11", "iPhone12,3": "iPhone 11 Pro", "iPhone12,5": "iPhone 11 Pro Max",
        "iPhone13,1": "iPhone 12 Mini", "iPhone13,2": "iPhone 12", "iPhone13,3": "iPhone 12 Pro", "iPhone13,4": "iPhone 12 Pro Max",
        "iPhone14,7": "iPhone 14", "iPhone14,8": "iPhone 14 Plus", "iPhone15,2": "iPhone 14 Pro", "iPhone15,3": "iPhone 14 Pro Max",
        "iPhone15,4": "iPhone 15", "iPhone15,5": "iPhone 15 Plus", "iPhone16,1": "iPhone 15 Pro", "iPhone16,2": "iPhone 15 Pro Max"
    }
    modelo_comercial = MODELOS.get(mod_tec, mod_tec)

    # 2. ISOLAR A PANIC STRING (Onde o erro real reside)
    # Vamos pegar apenas os primeiros 2000 caracteres do log onde o erro principal é descrito
    area_do_erro = conteudo[:2000].upper() 

    st.info(f"📱 **Aparelho:** {modelo_comercial}  |  📅 **Data do Log:** {data_log}")
    
    falha_encontrada = None

    # 3. BUSCA DE PRECISÃO (Para apenas no primeiro erro relevante encontrado)
    for erro, info in padroes.items():
        if erro.upper() in area_do_erro:
            falha_encontrada = (erro, info)
            break # PARA A BUSCA AQUI para não mostrar múltiplos resultados

    # 4. EXIBIÇÃO DOS 4 ITENS (Apenas se encontrou algo)
    if falha_encontrada:
        erro, info = falha_encontrada
        st.error(f"🚨 **Falha Detectada:** {erro}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**🔌 Periférico Alvo:**")
            st.subheader(info.get('periferico', 'Verificar'))
        
        with c2:
            st.write("**🛠 Causa:**")
            st.write(info.get('causa', 'N/A'))
        
        st.success(f"**💡 Dica do Chefinho:**\n\n{info.get('obs', 'N/A')}")
    else:
        st.warning("⚠️ Padrão não identificado. O log parece não conter erros conhecidos na área principal.")
        with st.expander("Ver log completo"):
            st.text(conteudo)
    
    st.write("---")
