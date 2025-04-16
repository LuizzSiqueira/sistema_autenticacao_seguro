import smtplib
import random
import string
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Função para gerar um token temporário para recuperação de senha
def generate_temp_password_token(length=6):
    """Gera um token temporário para recuperação de senha."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Função para enviar o e-mail de recuperação
def send_recovery_email(to_email, temp_token):
    """Envia um e-mail com um token temporário de recuperação de senha."""

    from_email = os.getenv("EMAIL_ADDRESS", "seu_email@gmail.com")
    from_password = os.getenv("EMAIL_PASSWORD", "sua_senha_do_email")  # Configure no .env

    subject = "Recuperação de Senha"
    body = f"Para recuperar sua senha, use o token temporário: {temp_token}"

    # Criação do e-mail
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conectando ao servidor SMTP e enviando o e-mail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Iniciar a criptografia TLS
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ E-mail enviado para {to_email} com o token de recuperação!")
    except Exception as e:
        print(f"❌ Falha ao enviar o e-mail: {str(e)}")
