import streamlit as st
from bancodedados import salvar_usuario 
from bancodedados import salvar_interacao 
from logica_chat import responder 

st.set_page_config(page_title="CHATBOT CRA UNINASSAU", layout="centered")

# logo da nassau para o avatar 
avatar_uninassau = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRu-WxeGPMERFd0TGfOBYXt5RtHi4nbT4F_bw&s" 


if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = {}
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
# tela inicial
col1, col2, col3 = st.columns([1, 3, 1])

with col2:

    st.image("imagens/uninassaulogo.svg", width=300) 

if not st.session_state["logado"]:
    st.markdown("<h1 style='text-align: center;'>Chatbot CRA - João Pessoa</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center;'>Informe seus dados para que possamos dar início a nossa conversa.</h5>", unsafe_allow_html=True)

    with st.form("form_cadastro", clear_on_submit=False):
        nome = st.text_input("Nome completo")
        tipo_usuario = st.selectbox("Você é:", ["aluno", "professor", "colaborador", "externo"])
        matricula = st.text_input("Matrícula (interno)") 
        email = st.text_input("E-mail")
        
        if st.form_submit_button("Iniciar conversa"):
            if not nome or not email:
                st.error("Por favor, preencha pelo menos o Nome e o E-mail.")
            else:
                usuario_id = salvar_usuario(nome, tipo_usuario, matricula, email)
                
                if usuario_id is not None:
                    st.session_state["logado"] = True
                    st.session_state["usuario"]["id"] = usuario_id
                    st.session_state["usuario"]["nome"] = nome
                    st.session_state["usuario"]["matricula"] = matricula 
                    st.rerun() 
                else:
                    st.error("Erro ao conectar ao banco de dados ou salvar usuário. Verifique se o MySQL está ativo e as credenciais.")

# tela de conversa
else:
    st.title("Chat Iniciado!")
    st.write(f"Conectado como: **{st.session_state['usuario']['nome']}**")

# mostra histórico
    for message in st.session_state["messages"]:

        avatar_role = avatar_uninassau if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar_role):
            st.markdown(message["content"])

# mostra entrada e processar resposta
    if prompt := st.chat_input("Digite sua dúvida aqui..."):
        
# adiciona e mostra a pergunta do usuário
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

# processa e mostra a resposta do assistente
        with st.chat_message("assistant", avatar=avatar_uninassau): 
            with st.spinner("O assistente está buscando a resposta..."):
                usuario_id = st.session_state["usuario"]["id"]
                resposta = responder(prompt, usuario_id)

            st.markdown(resposta)

# adiciona a resposta ao histórico
            st.session_state["messages"].append({"role": "assistant", "content": resposta})

# botão de sair na barra lateral
    with st.sidebar:
        if st.button("Sair e Encerrar Sessão"):
            st.session_state.clear()
            st.rerun()
