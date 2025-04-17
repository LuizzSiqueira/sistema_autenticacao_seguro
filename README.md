# 🔐 Módulo de Autenticação e Gestão de Usuários

## 📌 Objetivo

Este projeto tem como finalidade o desenvolvimento de um módulo de autenticação e gestão de usuários, reutilizável em diferentes sistemas. O foco é garantir segurança, conformidade com a LGPD e boas práticas de desenvolvimento, utilizando uma arquitetura modular e escalável.

---

## 🚀 Funcionalidades Implementadas

✅ Cadastro de novos usuários com validação de dados  
✅ Login de usuários com autenticação por nome de usuário e senha  
✅ Armazenamento seguro de senhas com hash usando bcrypt  
✅ Bloqueio de conta após múltiplas tentativas de login inválidas  
✅ Reset automático das tentativas após login bem-sucedido  
✅ Recuperação de senha com envio de token por e-mail  
✅ Validação de token para redefinição de senha  
✅ Estrutura modular organizada por camadas  
✅ Banco de dados SQLite funcional com persistência de dados  

---

## 📚 Especificações do Sistema

### 🔧 Requisitos Funcionais

- Cadastro de novos usuários com validação de dados
- Login de usuários com autenticação por e-mail e senha
- Autenticação via JWT com Access Token e Refresh Token
- Recuperação de senha via token temporário enviado por e-mail
- Edição e atualização de dados do perfil do usuário
- Atribuição de papéis e permissões (ex: administrador, usuário)
- Controle de sessões ativas (opcional)
- Registro de atividades de login e alterações
- Exclusão lógica de contas (LGPD)
- Anonimização de dados sensíveis

### 📈 Requisitos Não Funcionais

- Conformidade com a LGPD
- Respostas rápidas (< 1 segundo)
- API RESTful disponível
- Uso de JWT para autenticação
- Registro de falhas e tentativas inválidas
- Arquitetura modular
- Banco de dados relacional (atualmente SQLite)

---

## 🛠️ Funcionalidades Avançadas de Autenticação

### ✅ JWT com Access e Refresh Token (em desenvolvimento)
- Access Token: curta duração (~15 min)
- Refresh Token: longa duração (~7 dias)
- Endpoint de renovação: `POST /auth/refresh`
- Refresh token vinculado a usuário e IP

### 🔁 Recuperação de senha via e-mail
- Geração de token temporário com validade de 15 minutos
- Redefinição de senha com `POST /auth/reset`

---

## 🧠 Modelagem de Dados

### 🗂️ Tabelas principais

#### Usuário
- id_usuario (PK)
- nome
- email
- senha_hash
- data_criacao
- ultimo_login
- status

#### Perfil
- id_perfil (PK)
- nome

#### Permissão
- id_permissao (PK)
- nome
- descricao

#### Usuário_Permissão
- id_usuario (FK)
- id_permissao (FK)

#### Log_Acesso
- id_log (PK)
- id_usuario (FK)
- tipo
- data_hora
- ip_origem

#### Log_Alteracao
- id_log (PK)
- id_usuario (FK)
- campo_alterado
- valor_anterior
- valor_novo
- data_hora

---

## 📡 Endpoints RESTful

### 🔐 Autenticação
- `POST /auth/login` – Login e geração de tokens
- `POST /auth/refresh` – Renovação do Access Token
- `POST /auth/logout` – Logout e revogação
- `POST /auth/recover` – Envio de token para recuperação de senha
- `POST /auth/reset` – Redefinir senha com token temporário

### 👤 Usuários
- `POST /users`
- `GET /users/{id}`
- `PUT /users/{id}`
- `DELETE /users/{id}`

### 🔐 Permissões e Papéis
- `GET /permissions`
- `POST /permissions`
- `PUT /permissions/{id}`
- `GET /roles`
- `POST /roles`

### 📊 Logs
- `GET /logs/access`
- `GET /logs/changes`

---

## 🏗️ Arquitetura do Projeto

Estrutura modular dividida em camadas:

```bash
sistema_autenticacao_seguro/
├── python/
│   ├── controllers/       # Lógica de controle (auth_controller.py)
│   ├── db/                # Conexão com banco de dados (db.py)
│   ├── email/             # Envio de e-mails (email_utils.py)
│   ├── jwt/               # Geração/validação de JWT (jwt_handler.py)
│   ├── models/            # Usuários e dados (user.py)
│   └── main.py            # Interface CLI
└── database/
    └── users.db           # Banco SQLite (não versionar)


---

## ✅ Requisitos para rodar o projeto

- Python 3.10+
- Ambiente virtual recomendado
- `pip install -r requirements.txt`
- Banco de dados será criado automaticamente ao rodar o sistema

---

## ▶️ Como iniciar o projeto

```bash
# Clone o repositório
git clone git@github.com:LuizzSiqueira/sistema_autenticacao_seguro.git

# Acesse a pasta
cd sistema_autenticacao_seguro/python

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o sistema
python main.py
