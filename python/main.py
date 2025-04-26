import sys
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from getpass import getpass

# Adiciona o diretório raiz do projeto ao sys.path para evitar erro de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.models.user import (
    register_user, login_user, check_user_exists,
    recover_password, update_password
)

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.urandom(24)  # Necessário para flash messages

@app.route('/')
def index():
    """Página inicial do sistema de autenticação."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do usuário."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash("❌ Nome de usuário e senha são obrigatórios!")
            return redirect(url_for('login'))

        login_user(username, password)
        flash("✅ Login realizado com sucesso!")
        return redirect(url_for('index'))  # Redireciona para a página inicial após login

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de novo usuário."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash("❌ Todos os campos são obrigatórios!")
            return redirect(url_for('register'))

        if check_user_exists(username):
            flash(f"❌ O nome de usuário '{username}' já está em uso.")
            return redirect(url_for('register'))

        register_user(username, email, password)
        flash("✅ Registro realizado com sucesso!")
        return redirect(url_for('login'))  # Redireciona para a página de login após o registro

    return render_template('novo_usuario.html')

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    """Página de recuperação de senha."""
    if request.method == 'POST':
        email = request.form['email']
        
        if not email:
            flash("❌ O e-mail é obrigatório para recuperação!")
            return redirect(url_for('recover'))

        token = recover_password(None, email)  # Supondo que o nome de usuário não seja necessário aqui
        if token:
            flash("✅ Token enviado para o seu e-mail!")
            return redirect(url_for('reset_password', token=token))  # Redireciona para redefinir a senha
        else:
            flash("❌ Não foi possível enviar o token. Verifique seu e-mail.")
            return redirect(url_for('recover'))

    return render_template('recupera_senha.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Página para redefinir a senha após recuperação."""
    if request.method == 'POST':
        new_password = request.form['new_password']
        username = request.form['username']
        
        if not new_password or not username:
            flash("❌ Nome de usuário e nova senha são obrigatórios!")
            return redirect(url_for('reset_password', token=token))

        update_password(username, new_password, token, token)
        flash("✅ Senha atualizada com sucesso!")
        return redirect(url_for('login'))  # Redireciona para login após atualização de senha

    return render_template('redefinir_senha.html', token=token)

if __name__ == '__main__':
    app.run(debug=True)
