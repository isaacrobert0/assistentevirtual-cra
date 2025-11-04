from bancodedados import conectar

def responder(pergunta, usuario_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT resposta FROM faq WHERE pergunta LIKE %s", (f"%{pergunta}%",))
    resultado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if resultado:
        return resultado["resposta"]
    else:
        return "Questão ainda em processo de colocação no banco de dados..."
    
conexao = conectar()
if conexao is None:
    raise Exception("❌ Falha ao conectar ao banco. Verifique DATABASE_URL e logs do Render.")
cursor = conexao.cursor(dictionary=True)

