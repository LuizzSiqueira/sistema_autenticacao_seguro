from datetime import datetime
import socket
from python.db.db import connect_db

def get_ip_address():
    """Obtém o IP da máquina local."""
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Desconhecido"

def registrar_log(username, status):
    """Registra uma modificação ou evento relacionado ao usuário no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()

    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_origem = get_ip_address()

    cursor.execute(
        "INSERT INTO logs (username, status, data_hora, ip_origem) VALUES (?, ?, ?, ?)",
        (username, status, data_hora, ip_origem)
    )
    
    conn.commit()
    conn.close()
