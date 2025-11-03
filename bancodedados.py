import mysql.connector
from mysql.connector import Error

def conectar():
    try: 
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="chatbot_cra"
        )
        return conn
    except Error as e: 
        print("Erro ao conectar ao banco:", e)
        return None

def buscar_resposta(pergunta: str) -> str | None:
    conn = None  
    cursor = None
    
    try:
        conn = conectar()
        if conn is None:
            return None

        cursor = conn.cursor(dictionary=False) 
        
        sql = "SELECT resposta FROM faq WHERE pergunta LIKE %s LIMIT 1"
        cursor.execute(sql, (f"%{pergunta}%",)) 
        
        row = cursor.fetchone()
        
        if row: 
          return row[0] 
        return None

    except Error as e:
        print(f"Erro ao buscar resposta no MySQL: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def salvar_usuario(nome, tipo, matricula, email):
# salva pessoa que conversou com assistente no banco de dados
    conn = conectar()
    if conn is None:
        print("Conexão falhou")
        return None
    
    cursor = None 
    
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'tipo_usuario'")
        col_info = cursor.fetchone()
        print("SHOW COLUMNS ->", col_info)
        
        tipo_original = tipo
        if tipo is None:
            tipo = ""
        tipo = str(tipo).lower().strip()
        if tipo not in ("aluno", "professor", "colaborador", "externo"):
            print(f"Tipo inválido recebido: {repr(tipo_original)} -> será trocado para 'externo'")
            tipo = "externo"
        else:
            print(f"Tipo válido: {repr(tipo)}")
        
        matr_search = matricula if matricula and str(matricula).strip() else None
        email_search = email if email and str(email).strip() else None

        print("Valores de busca (matr_search, email_search):", (repr(matr_search), repr(email_search)))

        search_sql = "SELECT id FROM usuarios WHERE matricula = %s OR email = %s"
        cursor.execute(search_sql, (matr_search, email_search))
        result = cursor.fetchone()
        
        if result:
            print("Usuário já existe, id:", result[0])
            return result[0]  # usuário já existe, retorna o ID
        
        matr_val = matr_search
        email_val = email_search

        params = (nome, matr_val, email_val, tipo)
        print("Query INSERT params (nome, matricula, email, tipo):", tuple(repr(x) for x in params))

        sql = """
        INSERT INTO usuarios (nome, matricula, email, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, params)
        conn.commit()
        print("INSERT executado com sucesso. novo id:", cursor.lastrowid)
        return cursor.lastrowid
        
    except Error as e:
        print(f"Erro ao salvar/buscar usuário no MySQL: {e}")

        try:
            cursor.execute("SHOW WARNINGS")
            warnings = cursor.fetchall()
            print("WARNINGS:", warnings)
        except Exception:
            pass
        return None
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def salvar_interacao(usuario_id, mensagem, resposta):
# salva interacao com asisstente no banco de dados
    conn = conectar()
    if conn is None:
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        sql = """
        INSERT INTO interacoes (usuario_id, mensagem_usuario, resposta_chatbot)
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (usuario_id, mensagem, resposta))
        conn.commit()
        return True
    
    except Error as e:
        print(f"Erro ao salvar interação no MySQL: {e}")
        return False
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
