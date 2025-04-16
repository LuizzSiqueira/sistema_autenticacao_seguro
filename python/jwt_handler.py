import jwt
import datetime
from functools import wraps
from user import check_user_exists

SECRET_KEY = "supersecretkey"

# 1️⃣ Função para gerar o Access Token
def generate_access_token(username):
    """Gera um Access Token válido por 15 minutos."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    token = jwt.encode({'username': username, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

# 2️⃣ Função para gerar o Refresh Token
def generate_refresh_token(username):
    """Gera um Refresh Token válido por 7 dias."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    token = jwt.encode({'username': username, 'exp': expiration}, SECRET_KEY, algorithm='HS256')
    return token

# 3️⃣ Função para verificar o Access Token
def verify_access_token(token):
    """Verifica o Access Token e retorna os dados do usuário se válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# 4️⃣ Função para verificar o Refresh Token
def verify_refresh_token(token):
    """Verifica o Refresh Token e retorna os dados do usuário se válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
