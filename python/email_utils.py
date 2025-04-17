import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

# E-mail e senha do app diretamente no código
from_email = "central.seguranca.app@gmail.com"
from_password = "iuhl pemq gurn mqls"

def send_recovery_email(to_email, temp_token):
    """Envia um e-mail com um link de recuperação para o usuário."""
    
    if not from_email or not from_password:
        print("❌ E-mail ou senha de app não configurados corretamente.")
        return
    
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

def generate_temp_password_token():
    """Gera um token temporário para recuperação de senha."""
    # Gerando um token aleatório de 6 dígitos
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return token
