from user import register_user, login_user, check_user_exists, recover_password
from getpass import getpass

def menu():
    """Exibe o menu principal e retorna a escolha do usuário."""
    print("\n🔐 Bem-vindo ao sistema de autenticação!")
    print("1 - Registrar novo usuário")
    print("2 - Fazer login")
    print("3 - Recuperar senha")
    print("0 - Sair")
    return input("Digite o número da opção desejada: ").strip()

def executar_acao(opcao):
    """Executa a ação com base na opção do usuário."""
    if opcao not in ['1', '2', '3']:
        print("❌ Opção inválida! Por favor, escolha 1, 2, 3 ou 0.")
        return

    username = input("👤 Digite seu nome de usuário: ").strip()

    if not username:
        print("❌ Nome de usuário não pode estar vazio.")
        return

    if opcao == '1':
        if check_user_exists(username):
            print(f"❌ O nome de usuário '{username}' já está em uso.")
        else:
            password = getpass("🔒 Digite uma senha: ")
            register_user(username, password)

    elif opcao == '2':
        password = getpass("🔑 Digite sua senha: ")
        login_user(username, password)

    elif opcao == '3':
        recover_password(username)

def main():
    """Função principal para o fluxo do sistema."""
    while True:
        try:
            opcao = menu()
            if opcao == '0':
                print("👋 Saindo... Até logo!")
                break
            executar_acao(opcao)
        except Exception as e:
            print(f"⚠️ Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()
