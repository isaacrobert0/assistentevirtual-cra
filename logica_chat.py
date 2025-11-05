from bancodedados import conectar
from bancodedados import buscar_resposta, salvar_interacao

def responder(pergunta, usuario_id):
    # Busca no FAQ
    resposta = buscar_resposta(pergunta)
    if not resposta:
        resposta = "Desculpe, não encontrei uma resposta."
    
    # Salva a interação
    if usuario_id:
        salvar_interacao(usuario_id, pergunta, resposta)
    
    return resposta
    
conexao = conectar()
if conexao is None:
    raise Exception("Falha ao conectar ao banco. Verifique DATABASE_URL e logs do Render.")
cursor = conexao.cursor(dictionary=True)

