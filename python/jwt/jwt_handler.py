import jwt
import datetime
import os
from functools import wraps
from python.models.user import check_user_exists

# ==========================
# ⚙️ Configuração da Chave Secreta
# ==========================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # A chave secreta deve ser configurada em variáveis de ambiente para maior segurança


# =======================
# 🔑 Funções para Tokens
# =======================

def generate_access_token(username):
    """Gera um Access Token válido por 15 minutos."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    return _generate_token(username, expiration)


def generate_refresh_token(username):
    """Gera um Refresh Token válido por 7 dias."""
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return _generate_token(username, expiration)


def _generate_token(username, expiration):
    """Função genérica para gerar um token (access ou refresh)."""
    payload = {'username': username, 'exp': expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# ==========================
# 🔍 Funções de Verificação de Tokens
# ==========================

def verify_access_token(token):
    """Verifica o Access Token e retorna os dados do usuário se válido."""
    return _verify_token(token)


def verify_refresh_token(token):
    """Verifica o Refresh Token e retorna os dados do usuário se válido."""
    return _verify_token(token)


def _verify_token(token):
    """Função genérica para verificar a validade de qualquer token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Token expirado
    except jwt.InvalidTokenError:
        return None  # Token inválido


# =======================
# 🛡️ Decorators
# =======================

def token_required(f):
    """Decorator para verificar se o usuário está autenticado através do Access Token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = _get_token_from_request()

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


def _get_token_from_request():
    """Extrai o token da requisição (Authorization header)."""
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]  # Pega o token da requisição (Bearer <Token>)
    return token
