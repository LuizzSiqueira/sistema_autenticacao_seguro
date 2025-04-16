import bcrypt
from datetime import datetime, timedelta
from db import connect_db
from email_utils import send_recovery_email, generate_temp_password_token

def check_user_exists(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(username, password):
    if check_user_exists(username):
        return "Usuário já existe."

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()
    return "Usuário registrado com sucesso."

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, login_attempts, locked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        return "Usuário não encontrado."

    password_hash, attempts, locked_until = user

    if locked_until:
        locked_until = datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S.%f")
        if datetime.now() < locked_until:
            return f"Conta bloqueada até {locked_until.strftime('%H:%M:%S')}."

    if bcrypt.checkpw(password.encode(), password_hash):
        cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
        conn.commit()
        return "Login bem-sucedido."
    else:
        attempts += 1
        if attempts >= 3:
            bloqueio = datetime.now() + timedelta(minutes=5)
            cursor.execute("UPDATE users SET login_attempts = ?, locked_until = ? WHERE username = ?",
                           (attempts, bloqueio, username))
        else:
            cursor.execute("UPDATE users SET login_attempts = ? WHERE username = ?", (attempts, username))
        conn.commit()
        return f"Senha incorreta. Tentativas restantes: {3 - attempts if attempts < 3 else 0}"

def recover_password(username):
    if not check_user_exists(username):
        return "Usuário não encontrado."

    token = generate_temp_password_token()
    password_hash = bcrypt.hashpw(token.encode(), bcrypt.gensalt())

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ?, login_attempts = 0, locked_until = NULL WHERE username = ?",
                   (password_hash, username))
    conn.commit()
    conn.close()

    send_recovery_email(username, token)
    return "Nova senha enviada por e-mail."
