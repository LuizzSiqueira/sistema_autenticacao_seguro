import jwt
import datetime
import os
from functools import wraps
from python.user import check_user_exists

# Carregar a chave secreta do ambiente, se disponível
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # A chave secreta deve ser configurada em variáveis de ambiente para maior segurança

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
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

# 4️⃣ Função para verificar o Refresh Token
def verify_refresh_token(token):
    """Verifica o Refresh Token e retorna os dados do usuário se válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido

# 5️⃣ Decorator para proteger funções que requerem autenticação
def token_required(f):
    """Decorator para verificar se o usuário está autenticado através do Access Token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Pega o token da requisição (Bearer <Token>)

        if not token:
            return {"message": "Token is missing!"}, 403

        username = verify_access_token(token)
        if not username:
            return {"message": "Token is invalid or expired!"}, 403

        # Verificar se o usuário existe no banco
        if not check_user_exists(username):
            return {"message": "User not found!"}, 403

        return f(username, *args, **kwargs)
    
    return decorated_function
