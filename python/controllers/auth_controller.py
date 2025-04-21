import bcrypt
import socket
from datetime import datetime

from python.db.db import connect_db
from python.email.email_utils import send_recovery_email, generate_temp_password_token
from python.utils.log_utils import registrar_log_login


# ========================
# 🔒 Funções de Verificação
# ========================

def check_user_exists(username):
    """Verifica se o usuário já existe no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ============================
# 📝 Registro de Novo Usuário
# ============================

def register_user(username, password):
    """Realiza o registro de um novo usuário."""
    if check_user_exists(username):
        return "Usuário já existe."

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        return "Usuário registrado com sucesso."
    except Exception as e:
        conn.rollback()
        return f"Erro ao registrar usuário: {e}"
    finally:
        conn.close()


# ======================
# 🔐 Login de Usuário
# ======================

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    ip_origem = socket.gethostbyname(socket.gethostname())

    if not user:
        print("❌ Usuário não encontrado!")
        registrar_log_login(username, "nao_encontrado", ip_origem)
        return

    # Checar bloqueio por tentativas
    locked_until = user[5]
    if locked_until and datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S") > datetime.now():
        print(f"❌ Sua conta está bloqueada até {locked_until}.")
        registrar_log_login(username, "bloqueado", ip_origem)
        return

    stored_password_hash = user[3]

    try:
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print("✅ Login bem-sucedido!")
            registrar_log_login(username, "sucesso", ip_origem)
            reset_login_attempts(username)
        else:
            print("❌ Senha incorreta!")
            registrar_log_login(username, "falha", ip_origem)
            increment_login_attempts(username)
    except Exception as e:
        print(f"❌ Erro ao verificar a senha: {e}")
        registrar_log_login(username, "erro", ip_origem)


# ============================
# 🔄 Recuperação de Senha
# ============================

def recover_password(username):
    """Recupera a senha do usuário e envia um token por e-mail."""
    if not check_user_exists(username):
        return "Usuário não encontrado."

    token = generate_temp_password_token()
    password_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, login_attempts = 0, locked_until = NULL 
            WHERE username = ?
        """, (password_hash, username))
        conn.commit()
        send_recovery_email(username, token)
        return "Nova senha enviada por e-mail."
    except Exception as e:
        conn.rollback()
        return f"Erro ao recuperar a senha: {e}"
    finally:
        conn.close()
