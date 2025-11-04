import os
import mysql.connector
from urllib.parse import urlparse
from mysql.connector import Error
import unicodedata


def conectar():
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("DATABASE_URL não está definida!")
            return None
        print(f"DATABASE_URL lida: {db_url}")

        url = urlparse(db_url)
        conexao = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
        print("Conexão estabelecida!")
        return conexao
    except Error as e:
        print(f"Erro ao conectar: {e}")
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
        print("Usuário salvo com sucesso!")
        return True
    except Error as e:
        print("Erro ao salvar usuário:", e)
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
        print("Interação salva com sucesso!")
        return True
    except Error as e:
        print("Erro ao salvar interação:", e)
        return False


def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn')

def buscar_resposta(pergunta):
    conexao = conectar()
    if conexao is None:
        return None

    try:
        cursor = conexao.cursor(dictionary=True)
        sql = "SELECT resposta FROM faq"
        cursor.execute(sql)
        resultados = cursor.fetchall()
        cursor.close()
        conexao.close()

        pergunta_usuario = remover_acentos(pergunta.lower())
        for row in resultados:
            pergunta_db = remover_acentos(row["pergunta"].lower())
            if pergunta_usuario in pergunta_db:
                return row["resposta"]

        return None
    except Exception as e:
        print("Erro ao buscar resposta:", e)
        return None
    
def adicionar_faq(pergunta, resposta):
    conexao = conectar()
    if conexao is None:
        return False

    try:
        cursor = conexao.cursor()
        sql = "INSERT INTO faq (pergunta, resposta) VALUES (%s, %s)"
        cursor.execute(sql, (pergunta, resposta))
        conexao.commit()
        cursor.close()
        conexao.close()
        print("Pergunta e resposta adicionadas com sucesso!")
        return True
    except Exception as e:
        print("Erro ao adicionar FAQ:", e)
        return False
