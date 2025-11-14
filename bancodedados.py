import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse
from passlib.hash import bcrypt

def conectar():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL não encontrada!")
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
        print(f"Erro ao conectar ao banco: {e}")
        return None


def salvar_usuario(nome, tipo_usuario, matricula, email, senha=None):
    db = conectar()
    cursor = db.cursor()

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()) if senha else None

    sql = """
        INSERT INTO usuarios (nome, tipo_usuario, matricula, email, senha)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (nome, tipo_usuario, matricula, email, senha_hash))
    db.commit()

    novo_id = cursor.lastrowid

    cursor.close()
    db.close()
    return novo_id


def salvar_interacao(usuario_id, mensagem_usuario, resposta_chatbot):
    conexao = conectar()
    if not conexao:
        print("Falha ao conectar ao banco para salvar interação")
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

    return resultado[0] if resultado else None


def adicionar_faq(pergunta, resposta):
    conexao = conectar()
    if not conexao:
        print("Falha ao conectar ao banco para adicionar FAQ")
        return False

    try:
        cursor = conexao.cursor()
        sql = "INSERT INTO faq (pergunta, resposta) VALUES (%s, %s)"
        cursor.execute(sql, (pergunta, resposta))
        conexao.commit()
        cursor.close()
        conexao.close()
        print("FAQ adicionada com sucesso!")
        return True

    except Error as e:
        print("Erro ao adicionar FAQ:", e)
        if conexao:
            conexao.close()
        return False


def validar_login(email, senha_digitada):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()

    if usuario:
        senha_hash = usuario["senha"]
        return bcrypt.verify(senha_digitada, senha_hash)

    return False
