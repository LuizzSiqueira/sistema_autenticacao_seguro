import psycopg2
import os
from datetime import datetime
import socket

# Link de conexão com o Transaction Pooler
DB_URI = 'postgresql://postgres.hmrmyszfvftjcqmvpdym:pI15WkDX9cm6P6sV@aws-0-us-east-2.pooler.supabase.com:6543/postgres'
def connect_db():
    """Conecta ao banco de dados PostgreSQL no Supabase usando o Transaction Pooler."""
    try:
        conn = psycopg2.connect(DB_URI)
        print("Conexão bem-sucedida ao banco de dados.")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def close_db(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()
        print("Conexão fechada.")

def get_cursor(conn):
    """Obtém o cursor para executar comandos no banco."""
    return conn.cursor()

def registrar_log(username, status):
    """Registra logs de movimentações de usuários no PostgreSQL."""
    conn = connect_db()
    if conn is None:
        return  # Não registra log se a conexão falhar

    cursor = get_cursor(conn)
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        ip_origem = socket.gethostbyname(socket.gethostname())
    except:
        ip_origem = "127.0.0.1"  # Caso não consiga obter o IP, usa o local padrão

    try:
        # Executando o comando SQL para inserir o log
        cursor.execute('''
            INSERT INTO logs (username, status, data_hora, ip_origem)
            VALUES (%s, %s, %s, %s)
        ''', (username, status, data_hora, ip_origem))

        # Commit para garantir que a inserção seja salva
        conn.commit()
        print(f"Log registrado para o usuário {username}.")
    except Exception as e:
        print(f"Erro ao registrar log: {e}")
    finally:
        close_db(conn)
