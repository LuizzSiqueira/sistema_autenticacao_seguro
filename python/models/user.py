import bcrypt
from datetime import datetime, timedelta
from python.db.db import connect_db, registrar_log
from python.email.email_utils import send_recovery_email, generate_temp_password_token

def check_user_exists(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def check_email_exists(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, email, password):
    if check_user_exists(username) or check_email_exists(email):
        return

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, login_attempts, locked_until, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, email, password_hash.decode('utf-8'), 0, None, created_at)
    )
    conn.commit()
    conn.close()
    registrar_log(username, "Usuário registrado com sucesso")
    print(f"✅ Usuário '{username}' registrado com sucesso!")

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        if user[5] and datetime.strptime(user[5], "%Y-%m-%d %H:%M:%S") > datetime.now():
            print(f"❌ Conta bloqueada até {user[5]}")
            return False

        stored_password_hash = user[3]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            registrar_log(username, "Login bem-sucedido")
            reset_login_attempts(username)
            print("✅ Login bem-sucedido!")
            return True
        else:
            registrar_log(username, "Senha incorreta")
            increment_login_attempts(username)
            print("❌ Senha incorreta.")
            return False
    else:
        print("❌ Usuário não encontrado.")
        return False

def increment_login_attempts(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT login_attempts FROM users WHERE username = %s", (username,))
    login_attempts = cursor.fetchone()[0]

    if login_attempts >= 4:
        lock_account(username)
    else:
        cursor.execute("UPDATE users SET login_attempts = %s WHERE username = %s", (login_attempts + 1, username))

    conn.commit()
    conn.close()

def lock_account(username):
    conn = connect_db()
    cursor = conn.cursor()
    locked_until = datetime.now() + timedelta(minutes=10)
    cursor.execute("UPDATE users SET locked_until = %s WHERE username = %s",
                   (locked_until.strftime("%Y-%m-%d %H:%M:%S"), username))
    conn.commit()
    conn.close()
    registrar_log(username, "Conta bloqueada por falhas de login")

def reset_login_attempts(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = %s", (username,))
    conn.commit()
    conn.close()

def recover_password(username, email):
    if check_email_exists(email):
        token = generate_temp_password_token()
        send_recovery_email(email, token)
        registrar_log(username, "Token de recuperação enviado")
        return token
    else:
        registrar_log(username, "Tentativa de recuperação com e-mail inválido")
        return None

def update_password(username, new_password, token_entered, valid_token):
    if token_entered == valid_token:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s",
                       (password_hash.decode('utf-8'), username))
        conn.commit()
        conn.close()
        registrar_log(username, "Senha atualizada com sucesso")
    else:
        registrar_log(username, "Token de redefinição inválido")
        print("❌ Token de redefinição inválido.")