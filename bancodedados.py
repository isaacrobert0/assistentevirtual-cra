import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse
import os
import bcrypt

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
    if not db:
        return None

    cursor = db.cursor()
    
    if senha:
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode()
    else:
        senha_hash = None

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

def validar_login(email, senha_digitada):
    conexao = conectar()
    if not conexao:
        return None

    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()

    if not usuario or not usuario["senha"]:
        return None

    senha_hash = usuario["senha"].encode()

    if bcrypt.checkpw(senha_digitada.encode("utf-8"), senha_hash):
        return usuario
    else:
        return None


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
        return True
    except Error as e:
        print("Erro ao adicionar FAQ:", e)
        if conexao:
            conexao.close()
        return False

def buscar_resposta(pergunta):
    conexao = conectar()
    if not conexao:
        return None

    try:
        cursor = conexao.cursor()
        sql = "SELECT resposta FROM faq WHERE pergunta LIKE %s"
        cursor.execute(sql, (f"%{pergunta}%",))
        resultado = cursor.fetchone()
        cursor.close()
        conexao.close()
        return resultado[0] if resultado else None
    except Exception as e:
        print("Erro ao buscar resposta:", e)
        if conexao:
            conexao.close()
        return None