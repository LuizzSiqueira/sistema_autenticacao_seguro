import sqlite3
import os
from datetime import datetime
import socket

# Caminho absoluto para o banco de dados (evita erro "unable to open database file")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório do arquivo atual
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'database', 'users.db'))

def connect_db():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_PATH)

def close_db(conn):
    """Fecha a conexão com o banco de dados."""
    if conn:
        conn.close()

def get_cursor(conn):
    """Obtém o cursor para executar comandos no banco."""
    return conn.cursor()

def registrar_log(username, status):
    """Registra logs de movimentações de usuários."""
    conn = connect_db()
    cursor = conn.cursor()

    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        ip_origem = socket.gethostbyname(socket.gethostname())
    except:
        ip_origem = "127.0.0.1"

    cursor.execute('''
        INSERT INTO logs (username, status, data_hora, ip_origem)
        VALUES (?, ?, ?, ?)
    ''', (username, status, data_hora, ip_origem))

    conn.commit()
    close_db(conn)