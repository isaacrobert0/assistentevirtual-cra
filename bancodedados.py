import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse

def conectar():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL não encontrada!")
        return None

    try:
        url = urlparse(db_url)
        conexao = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )

        return conexao
    except Error as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None


def salvar_usuario(nome, tipo_usuario, matricula, email):
    conexao = conectar()
    if not conexao:
        return None
    try:
        cursor = conexao.cursor()
        sql = """
        INSERT INTO usuarios (nome, matricula, email, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (nome, matricula, email, tipo_usuario))
        conexao.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        conexao.close()
        return usuario_id
    except Error as e:
        print("❌ Erro ao salvar usuário:", e)
        return None


def salvar_interacao(usuario_id, mensagem_usuario, resposta_chatbot):
    conexao = conectar()
    if not conexao:
        print("❌ Falha ao conectar ao banco para salvar interação")
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
        return True
    except Exception as e:
        print("Erro ao salvar interação:", e)
        if conexao:
            conexao.close()
        return False
    
def buscar_resposta(pergunta):
        con = conectar()
        cursor = con.cursor()
        cursor.execute("SELECT resposta FROM faq WHERE pergunta LIKE %s", (f"%{pergunta}%",))
        resultado = cursor.fetchone()
        con.close()

        if resultado:
            return resultado[0]
        else:
            return None

def adicionar_faq(pergunta, resposta):
    conexao = conectar()
    if not conexao:
        print("❌ Falha ao conectar ao banco para adicionar FAQ")
        return False

    try:
        cursor = conexao.cursor()
        sql = "INSERT INTO faq (pergunta, resposta) VALUES (%s, %s)"
        cursor.execute(sql, (pergunta, resposta))
        conexao.commit()
        cursor.close()
        conexao.close()
        print("✅ FAQ adicionada com sucesso!")
        return True
    except Error as e:
        print("❌ Erro ao adicionar FAQ:", e)
        if conexao:
            conexao.close()
        return False
