from passlib.hash import bcrypt
import mysql.connector
from mysql.connector import Error
import os
from urllib.parse import urlparse

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

    senha_hash = bcrypt.hash(senha) if senha else None 

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

def validar_login(email, senha_digitada):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()

    if not usuario or not usuario["senha"]:
        return False

    senha_hash = usuario["senha"]
    return bcrypt.verify(senha_digitada, senha_hash)
