import bcrypt
from datetime import datetime, timedelta
from python.db import connect_db
from python.email_utils import send_recovery_email, generate_temp_password_token

def check_user_exists(username):
    """Verifica se o usuário já existe no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(username, password):
    """Realiza o registro de um novo usuário."""
    if check_user_exists(username):
        return "Usuário já existe."

    # Gerar o hash da senha
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Erro ao registrar usuário: {e}"
    conn.close()
    return "Usuário registrado com sucesso."

def login_user(username, password):
    """Realiza o login do usuário."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, login_attempts, locked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "Usuário não encontrado."

    password_hash, attempts, locked_until = user

    if locked_until:
        locked_until = datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() < locked_until:
            conn.close()
            return f"Conta bloqueada até {locked_until.strftime('%H:%M:%S')}."

    # Verificar a senha
    if bcrypt.checkpw(password.encode(), password_hash):
        # Resetar tentativas de login e desbloquear a conta
        cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return "Login bem-sucedido."
    else:
        # Incrementar tentativas de login
        attempts += 1
        if attempts >= 3:
            bloqueio = datetime.now() + timedelta(minutes=5)
            cursor.execute("UPDATE users SET login_attempts = ?, locked_until = ? WHERE username = ?",
                           (attempts, bloqueio, username))
        else:
            cursor.execute("UPDATE users SET login_attempts = ? WHERE username = ?", (attempts, username))
        conn.commit()
        conn.close()
        return f"Senha incorreta. Tentativas restantes: {3 - attempts if attempts < 3 else 0}"

def recover_password(username):
    """Recupera a senha do usuário e envia um token por e-mail."""
    if not check_user_exists(username):
        return "Usuário não encontrado."

    # Gerar um token temporário
    token = generate_temp_password_token()

    # Gerar o hash do token
    password_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Atualizar a senha do usuário no banco de dados com o token gerado
        cursor.execute("UPDATE users SET password_hash = ?, login_attempts = 0, locked_until = NULL WHERE username = ?",
                       (password_hash, username))
        conn.commit()
        send_recovery_email(username, token)  # Enviar o e-mail de recuperação
        conn.close()
        return "Nova senha enviada por e-mail."
    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Erro ao recuperar a senha: {e}"
