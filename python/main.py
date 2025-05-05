import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Ajuste do path para imports internos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.models.user import (
    register_user, login_user, check_user_exists,
    recover_password, update_password
)
from python.db.db import connect_db

# ===============================
# 🔧 Configuração do Flask
# ===============================
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.urandom(24)

# ===============================
# 🔐 Funções de Autenticação
# ===============================
def is_authenticated():
    return 'username' in session

def get_user_permissions(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT permission_name FROM permissions WHERE username = %s", (username,))
    permissions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return permissions

# ===============================
# 🌐 Rotas da Aplicação
# ===============================
@app.route('/')
def index():
    if is_authenticated():
        return redirect(url_for('painel_usuarios', username=session['username']))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("❌ Nome de usuário e senha são obrigatórios!")
            return redirect(url_for('login'))

        if login_user(username, password):
            session['username'] = username
            session['permissions'] = get_user_permissions(username)
            flash("✅ Login realizado com sucesso!")
            return redirect(url_for('painel_usuarios', username=username))
        else:
            flash("❌ Falha no login. Verifique suas credenciais!")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("❌ Todos os campos são obrigatórios!")
            return redirect(url_for('register'))

        if check_user_exists(username):
            flash(f"❌ O nome de usuário '{username}' já está em uso.")
            return redirect(url_for('register'))

        register_user(username, email, password)
        flash("✅ Registro realizado com sucesso!")
        return redirect(url_for('login'))

    return render_template('novo_usuario.html')

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("❌ O e-mail é obrigatório para recuperação!")
            return redirect(url_for('recover'))

        token = recover_password(None, email)
        if token:
            flash("✅ Token enviado para o seu e-mail!")
            return redirect(url_for('reset_password', token=token))
        else:
            flash("❌ Não foi possível enviar o token. Verifique seu e-mail.")

    return render_template('recupera_senha.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')

        if not username or not new_password:
            flash("❌ Nome de usuário e nova senha são obrigatórios!")
            return redirect(url_for('reset_password', token=token))

        update_password(username, new_password, token, token)
        flash("✅ Senha atualizada com sucesso!")
        return redirect(url_for('login'))

    return render_template('redefinir_senha.html', token=token)

@app.route('/painel/<username>')
def painel_usuarios(username):
    if not is_authenticated() or session.get('username') != username:
        flash("⚠️ Sessão inválida. Faça login novamente.")
        return redirect(url_for('login'))

    permissoes = session.get('permissions', [])
    return render_template('painel_usuarios.html', username=username, permissoes=permissoes)

@app.route('/executar_permissao', methods=['POST'])
def executar_permissao():
    username = session.get('username')
    permissao = request.form.get('permissao')

    if not username or not permissao:
        flash("⚠️ Ação não autorizada.")
        return redirect(url_for('login'))

    flash(f"✅ {username} executou a permissão: {permissao}")
    return redirect(url_for('painel_usuarios', username=username))

@app.route('/gerenciar_permissoes', methods=['GET', 'POST'])
def gerenciar_permissoes():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        permissao = request.form.get('permissao')

        # TODO: lógica de atualização real no banco
        flash("✅ Permissões atualizadas com sucesso!")

    return render_template('gerenciar_permissoes.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("🚪 Logout realizado com sucesso.")
    return redirect(url_for('login'))

# ===============================
# ▶️ Execução
# ===============================
if __name__ == '__main__':
    app.run(debug=True)
