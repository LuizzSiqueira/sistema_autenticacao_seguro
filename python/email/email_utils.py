import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os

# ========================
# ⚙️ Configuração do E-mail
# ========================

# Usar variáveis de ambiente para as credenciais de e-mail
FROM_EMAIL = os.getenv("FROM_EMAIL", "central.seguranca.app@gmail.com")
FROM_PASSWORD = os.getenv("FROM_PASSWORD", "iuhl pemq gurn mqls")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_recovery_email(to_email, temp_token):
    """Envia um e-mail com um link de recuperação para o usuário."""
    if not FROM_EMAIL or not FROM_PASSWORD:
        print("❌ E-mail ou senha de app não configurados corretamente.")
        return

    subject = "Recuperação de Senha"
    body = f"Para recuperar sua senha, use o token temporário: {temp_token}"

    # Criar a mensagem do e-mail
    msg = create_email_message(subject, body, to_email)

    try:
        # Enviar o e-mail
        send_email(msg)
        print(f"✅ E-mail enviado para {to_email} com o token de recuperação!")
    except Exception as e:
        print(f"❌ Falha ao enviar o e-mail: {str(e)}")


def create_email_message(subject, body, to_email):
    """Cria e retorna a mensagem de e-mail."""
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    return msg


def send_email(msg):
    """Envia a mensagem de e-mail através do servidor SMTP configurado."""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Iniciar a criptografia TLS
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.sendmail(FROM_EMAIL, msg['To'], msg.as_string())
    except Exception as e:
        raise Exception(f"Erro ao enviar o e-mail: {str(e)}")


# ==========================
# 🔑 Função de Geração de Token
# ==========================

def generate_temp_password_token():
    """Gera um token temporário de 6 dígitos para recuperação de senha."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
