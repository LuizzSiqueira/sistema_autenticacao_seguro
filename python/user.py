import bcrypt
from db import connect_db
from datetime import datetime, timedelta
from email_utils import send_recovery_email, generate_temp_password_token

# Função para verificar se o usuário já existe no banco de dados
def check_user_exists(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Função para verificar se o e-mail está associado a um usuário no banco de dados
def check_email_exists(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Função para registrar um novo usuário
def register_user(username, email, password):
    if check_user_exists(username):
        print(f"❌ O nome de usuário '{username}' já está em uso.")
        return
    if check_email_exists(email):
        print(f"❌ O e-mail '{email}' já está em uso.")
        return
    
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, login_attempts, locked_until) VALUES (?, ?, ?, ?, ?)", 
        (username, email, password_hash.decode('utf-8'), 0, None)
    )
    conn.commit()
    conn.close()
    print(f"✅ Usuário '{username}' registrado com sucesso!")

# Função para realizar o login do usuário
def login_user(username, password):
    """Realiza o login do usuário existente."""
    conn = connect_db()
    cursor = conn.cursor()

    # Buscando o usuário pelo nome de usuário
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Verifica bloqueio
        if user[5] and datetime.strptime(user[5], "%Y-%m-%d %H:%M:%S") > datetime.now():
            print(f"❌ Sua conta está bloqueada até {user[5]}.")
            return

        stored_password_hash = user[3]

        try:
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                print("✅ Login bem-sucedido!")
                reset_login_attempts(username)
            else:
                print("❌ Senha incorreta!")
                increment_login_attempts(username)
        except Exception as e:
            print(f"❌ Erro ao verificar a senha: {e}")
    else:
        print("❌ Usuário não encontrado!")

# Função para incrementar tentativas de login
def increment_login_attempts(username):
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

# Função para bloquear conta por 10 minutos após 5 falhas
def lock_account(username):
    conn = connect_db()
    cursor = conn.cursor()
    locked_until = datetime.now() + timedelta(minutes=10)
    cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?", 
                   (locked_until.strftime("%Y-%m-%d %H:%M:%S"), username))
    conn.commit()
    conn.close()
    print("❌ Sua conta foi bloqueada por 10 minutos devido a múltiplas tentativas falhas.")

# Função para resetar tentativas de login
def reset_login_attempts(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET login_attempts = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Geração e envio do token de recuperação
def recover_password(username, email):
    if check_email_exists(email):
        token = generate_temp_password_token()
        send_recovery_email(email, token)
        print("✅ Token de recuperação enviado com sucesso!")
        return token
    else:
        print("❌ E-mail não encontrado!")
        return None

# Atualização de senha com validação de token
def update_password(username, new_password, token_entered, valid_token):
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
    else:
        print("❌ Token inválido. Tente novamente.")
