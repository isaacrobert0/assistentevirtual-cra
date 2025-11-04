import os
import mysql.connector
from urllib.parse import urlparse
from mysql.connector import Error

def conectar():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL não está definida!")
            return None
        print(f"🌐 DATABASE_URL lida: {db_url}")  # debug

        url = urlparse(db_url)
        conexao = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
        print("✅ Conexão estabelecida!")
        return conexao
    except Error as e:
        print(f"❌ Erro ao conectar: {e}")
        return None


def salvar_usuario(nome, matricula, email, tipo_usuario):
    conexao = conectar()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        sql = """
        INSERT INTO usuarios (nome, matricula, email, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (nome, matricula, email, tipo_usuario))
        conexao.commit()
        cursor.close()
        conexao.close()
        print("✅ Usuário salvo com sucesso!")
        return True
    except Error as e:
        print("❌ Erro ao salvar usuário:", e)
        return False


def salvar_interacao(usuario_id, mensagem_usuario, resposta_chatbot):
    conexao = conectar()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        sql = """
        INSERT INTO interacoes (usuario_id, mensagem_usuario, resposta_chatbot)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (usuario_id, mensagem_usuario, resposta_chatbot))
        conexao.commit()
        cursor.close()
        conexao.close()
        print("💬 Interação salva com sucesso!")
        return True
    except Error as e:
        print("❌ Erro ao salvar interação:", e)
        return False


def buscar_resposta(pergunta):
    conexao = conectar()
    if conexao is None:
        return None

    try:
        cursor = conexao.cursor(dictionary=True)
        sql = "SELECT resposta FROM faq WHERE LOWER(pergunta) LIKE %s"
        cursor.execute(sql, (f"%{pergunta.lower()}%",))
        resultado = cursor.fetchone()
        cursor.close()
        conexao.close()

        if resultado:
            return resultado["resposta"]
        else:
            return None
    except Error as e:
        print("❌ Erro ao buscar resposta:", e)
        return None
