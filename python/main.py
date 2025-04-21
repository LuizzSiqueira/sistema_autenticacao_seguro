import sys
import os
import bcrypt
from getpass import getpass

# Adiciona o diretório raiz do projeto ao sys.path para evitar erro de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.models.user import (
    register_user, login_user, check_user_exists,
    recover_password, update_password
)

def menu():
    """Exibe o menu principal e retorna a escolha do usuário."""
    print("\n🔐 Bem-vindo ao sistema de autenticação!")
    print("1 - Registrar novo usuário")
    print("2 - Fazer login")
    print("3 - Recuperar senha")
    print("0 - Sair")
    
    opcao = input("Digite o número da opção desejada: ").strip()

    if opcao not in ['0', '1', '2', '3']:
        print("❌ Opção inválida! Por favor, escolha 1, 2, 3 ou 0.")
        return None
    
    return opcao

def executar_acao(opcao):
    """Executa a ação com base na opção do usuário."""
    if opcao == '0':
        return

    username = input("👤 Digite seu nome de usuário: ").strip()
    if not username:
        print("❌ Nome de usuário não pode estar vazio.")
        return

    if opcao == '1':  # Registrar novo usuário
        if check_user_exists(username):
            print(f"❌ O nome de usuário '{username}' já está em uso.")
        else:
            email = input("📧 Digite seu e-mail: ").strip()
            if not email:
                print("❌ O e-mail não pode estar vazio.")
                return

            password = getpass("🔒 Digite uma senha: ")
            register_user(username, email, password)

    elif opcao == '2':  # Fazer login
        password = getpass("🔑 Digite sua senha: ")
        login_user(username, password)

    elif opcao == '3':  # Recuperar senha
        email = input("📧 Digite seu e-mail para recuperação de senha: ").strip()
        if not email:
            print("❌ O e-mail não pode estar vazio.")
            return

        token = recover_password(username, email)
        if token:
            token_entered = input("Digite o token recebido no seu e-mail: ").strip()
            new_password = getpass("Digite sua nova senha: ")
            update_password(username, new_password, token_entered, token)

def main():
    """Função principal para o fluxo do sistema."""
    while True:
        try:
            opcao = menu()
            if opcao == '0':
                print("👋 Saindo... Até logo!")
                break
            if opcao is not None:
                executar_acao(opcao)
        except Exception as e:
            print(f"⚠️ Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
