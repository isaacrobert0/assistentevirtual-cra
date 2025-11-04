import streamlit as st
from bancodedados import salvar_usuario, salvar_interacao
from logica_chat import responder

st.set_page_config(page_title="CHATBOT CRA UNINASSAU", layout="centered")

# Logo da nassau para o avatar 
avatar_uninassau = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRu-WxeGPMERFd0TGfOBYXt5RtHi4nbT4F_bw&s" 

# Lista de usuários do CRA autorizados
usuarios_autorizados = {
    "cra@uninassau.edu.br": "cra@uni2003"
}

# Sessão do Streamlit
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["usuario"] = None

# Tela de login
if not st.session_state["logado"]:
    st.subheader("Login CRA")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if email in usuarios_autorizados and usuarios_autorizados[email] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = email
            st.success(f"Bem-vindo, {email}!")
        else:
            st.error("Email ou senha inválidos")

# Inicialização de variáveis de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = {}
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Tela inicial
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

# Tela de conversa e cadastro CRA
else:
    st.title("Chat Iniciado!")
    st.write(f"Conectado como: **{st.session_state['usuario']['nome']}**")

    # Formulário de cadastro de perguntas/respostas (somente CRA)
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
