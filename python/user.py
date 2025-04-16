import bcrypt
import sqlite3
from db import connect_db
from datetime import datetime, timedelta
from email import send_recovery_email, generate_temp_password_token

# Função para verificar se o usuário já existe no banco de dados
def check_user_exists(username):
    """Verifica se o usuário já existe no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    conn.close()
    return user

# Função para registrar um novo usuário
def register_user(username, password):
    """Realiza o registro de um novo usuário."""
    if check_user_exists(username):
        print(f"❌ O nome de usuário '{username}' já está em uso.")
        return
    
    # Gerar SALT e hash da senha
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                   (username, password_hash.decode('utf-8')))
    
    conn.commit()
    conn.close()
    print(f"✅ Usuário '{username}' registrado com sucesso!")

# Função para realizar o login do usuário
def login_user(username, password):
    """Realiza o login do usuário existente."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        # Verificar se a conta está bloqueada
        if user[4] and datetime.strptime(user[4], "%Y-%m-%d %H:%M:%S") > datetime.now():
            print(f"❌ Sua conta está bloqueada até {user[4]}. Tente novamente depois.")
            return

        # Verificar a senha
        stored_password_hash = user[2]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            print("✅ Login bem-sucedido!")
            reset_login_attempts(username)
        else:
            print("❌ Senha incorreta!")
            increment_login_attempts(username)
    else:
        print("❌ Usuário não encontrado!")

# Função para incrementar a contagem de tentativas de login
def increment_login_attempts(username):
    """Incrementa o número de tentativas de login e bloqueia a conta após 5 tentativas falhas."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT login_attempts FROM users WHERE username = ?", (username,))
    login_attempts = cursor.fetchone()[0]
    
    if login_attempts >= 4:
        lock_account(username)
    else:
        cursor.execute("UPDATE users SET login_attempts = ? WHERE username = ?", 
                       (login_attempts + 1, username))
    
    conn.commit()
    conn.close()

# Função para bloquear a conta por 10 minutos após 5 tentativas falhas
def lock_account(username):
    """Bloqueia a conta do usuário por 10 minutos após 5 tentativas falhas."""
    conn = connect_db()
    cursor = conn.cursor()
    
    locked_until = datetime.now() + timedelta(minutes=10)
    cursor.execute("UPDATE users SET locked_until = ? WHERE username = ?", 
                   (locked_until.strftime("%Y-%m-%d %H:%M:%S"), username))
    
    conn.commit()
    conn.close()
    print("❌ Sua conta foi bloqueada por 10 minutos devido a múltiplas tentativas falhas.")

# Função para resetar a contagem de tentativas de login
def reset_login_attempts(username):
    """Reseta a contagem de tentativas de login após um login bem-sucedido."""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE users SET login_attempts = 0 WHERE username = ?", (username,))
    
    conn.commit()
    conn.close()

# Função para gerar e enviar o token de recuperação
def recover_password(username):
    """Gera o token de recuperação e envia por e-mail."""
    if check_user_exists(username):
        token = generate_temp_password_token()
        send_recovery_email(username, token)
        print("✅ Token de recuperação enviado com sucesso!")
    else:
        print("❌ Usuário não encontrado!")

# Função para atualizar a senha
def update_password(username, new_password):
    """Atualiza a senha do usuário no banco de dados."""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash.decode('utf-8'), username))
    conn.commit()
    conn.close()
    print(f"✅ Senha de '{username}' atualizada com sucesso!")
