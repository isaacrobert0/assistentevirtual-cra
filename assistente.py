import streamlit as st
from bancodedados import salvar_usuario, salvar_interacao
from logica_chat import responder

st.set_page_config(page_title="CHATBOT CRA UNINASSAU", layout="centered")

# Avatar e logo
avatar_uninassau = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRu-WxeGPMERFd0TGfOBYXt5RtHi4nbT4F_bw&s" 

# Sessão do Streamlit
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = {}
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "cra_logado" not in st.session_state:
    st.session_state["cra_logado"] = False
if "cra_usuario" not in st.session_state:
    st.session_state["cra_usuario"] = None

# Layout inicial
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image("imagens/uninassaulogo.svg", width=300) 

# Título
st.markdown("<h1 style='text-align: center;'>Chatbot CRA - João Pessoa</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Informe seus dados para iniciar a conversa ou faça login CRA para cadastrar perguntas.</h5>", unsafe_allow_html=True)

# Formulário de cadastro do usuário normal
if not st.session_state["logado"]:
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
                    st.error("Erro ao conectar ao banco de dados ou salvar usuário.")

# Login separado para o CRA na barra lateral
st.sidebar.subheader("Login CRA (somente colaboradores)")
email_cra = st.sidebar.text_input("Email CRA")
senha_cra = st.sidebar.text_input("Senha CRA", type="password")
if st.sidebar.button("Entrar CRA"):
    usuarios_autorizados = {
        "isaac@uninassau.edu.br": "senha123",
        "maria@uninassau.edu.br": "senha456",
    }
    if email_cra in usuarios_autorizados and senha_cra == usuarios_autorizados[email_cra]:
        st.session_state["cra_logado"] = True
        st.session_state["cra_usuario"] = email_cra
        st.success(f"Logado como CRA: {email_cra}")
    else:
        st.error("Email ou senha CRA inválidos")

# Tela de conversa
if st.session_state["logado"]:
    st.title("Chat Iniciado!")
    st.write(f"Conectado como: **{st.session_state['usuario']['nome']}**")

    # Formulário de cadastro de perguntas/respostas (somente CRA)
    if st.session_state["cra_logado"]:
        with st.expander("Cadastrar nova pergunta (somente CRA)"):
            pergunta = st.text_input("Pergunta")
            resposta = st.text_area("Resposta")
            if st.button("Cadastrar Pergunta"):
                if pergunta and resposta:
                    from bancodedados import adicionar_faq
                    sucesso = adicionar_faq(pergunta, resposta)
                    if sucesso:
                        st.success("✅ Pergunta e resposta cadastradas com sucesso!")
                    else:
                        st.error("❌ Erro ao cadastrar. Verifique a conexão com o banco.")
                else:
                    st.warning("⚠️ Preencha tanto a pergunta quanto a resposta.")

    # Mostra histórico do chat
    for message in st.session_state["messages"]:
        avatar_role = avatar_uninassau if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar_role):
            st.markdown(message["content"])

    # Entrada do chat e processamento da resposta
    if prompt := st.chat_input("Digite sua dúvida aqui..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=avatar_uninassau):
            with st.spinner("O assistente está buscando a resposta..."):
                usuario_id = st.session_state["usuario"]["id"]
                resposta = responder(prompt, usuario_id)
            st.markdown(resposta)

        st.session_state["messages"].append({"role": "assistant", "content": resposta})

# Botão de sair na barra lateral
with st.sidebar:
    if st.button("Sair e Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()
