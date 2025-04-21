import bcrypt
from python.db.db import connect_db
from datetime import datetime, timedelta
from python.email.email_utils import send_recovery_email, generate_temp_password_token
from python.db.db import connect_db, registrar_log


# ============================
# 🔑 Funções de Verificação
# ============================

def check_user_exists(username):
    """Verifica se o usuário já existe no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def check_email_exists(email):
    """Verifica se o e-mail está associado a um usuário no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


# ============================
# ✍️ Funções de Registro
# ============================

def register_user(username, email, password):
    """Registra um novo usuário."""
    if check_user_exists(username):
        print(f"❌ O nome de usuário '{username}' já está em uso.")
        return
    if check_email_exists(email):
        print(f"❌ O e-mail '{email}' já está em uso.")
        return

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    # Obtém a data e hora atual para o campo 'created_at'
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, login_attempts, locked_until, created_at) VALUES (?, ?, ?, ?, ?, ?)", 
        (username, email, password_hash.decode('utf-8'), 0, None, created_at)
    )
    conn.commit()
    conn.close()
    registrar_log(username, "Usuário registrado com sucesso")
    print(f"✅ Usuário '{username}' registrado com sucesso!")



# ============================
# 🔒 Funções de Login e Bloqueio
# ============================

def login_user(username, password):
    """Realiza o login do usuário existente."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Verifica bloqueio
        if user[5] and datetime.strptime(user[5], "%Y-%m-%d %H:%M:%S") > datetime.now():
            print(f"❌ Sua conta está bloqueada até {user[5]}.")
            return

        stored_password_hash = user[3]

        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print("✅ Login bem-sucedido!")
            registrar_log(username, "Login bem-sucedido")
            reset_login_attempts(username)
        else:
            print("❌ Senha incorreta!")
            registrar_log(username, "Senha incorreta")
            increment_login_attempts(username)
    else:
        print("❌ Usuário não encontrado!")
        registrar_log(username, "Usuário não encontrado")


def increment_login_attempts(username):
    """Incrementa tentativas de login e bloqueia se atingir o limite."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT login_attempts FROM users WHERE username = ?", (username,))
    login_attempts = cursor.fetchone()[0]

    if login_attempts >= 4:
        lock_account(username)
    else:
        cursor.execute("UPDATE users SET login_attempts = ? WHERE username = ?", (login_attempts + 1, username))
    
    conn.commit()
    conn.close()


def lock_account(username):
    """Bloqueia a conta por 10 minutos após 5 falhas de login."""
    conn = connect_db()
    cursor = conn.cursor()
    locked_until = datetime.now() + timedelta(minutes=10)
    cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?", 
                   (locked_until.strftime("%Y-%m-%d %H:%M:%S"), username))
    conn.commit()
    conn.close()
    registrar_log(username, "Conta bloqueada por 10 minutos")
    print("❌ Sua conta foi bloqueada por 10 minutos devido a múltiplas tentativas falhas.")


def reset_login_attempts(username):
    """Reseta tentativas de login e desbloqueia o usuário."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET login_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
    conn.commit()
    conn.close()


# ============================
# 🔑 Funções de Recuperação de Senha
# ============================

def recover_password(username, email):
    """Gera e envia um token de recuperação de senha."""
    if check_email_exists(email):
        token = generate_temp_password_token()
        send_recovery_email(email, token)
        print("✅ Token de recuperação enviado com sucesso!")
        registrar_log(username, "Token de recuperação enviado")
        return token
    else:
        print("❌ E-mail não encontrado!")
        registrar_log(username, "Tentativa de recuperação com e-mail inválido")
        return None


def update_password(username, new_password, token_entered, valid_token):
    """Atualiza a senha se o token for válido."""
    if token_entered == valid_token:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                       (password_hash.decode('utf-8'), username))
        conn.commit()
        conn.close()
        print(f"✅ Senha de '{username}' atualizada com sucesso!")
        registrar_log(username, "Senha alterada com sucesso")
    else:
        print("❌ Token inválido. Tente novamente.")
        registrar_log(username, "Tentativa de redefinição com token inválido")
