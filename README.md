# Django_API_RESTful
# E-commerce API

Esta é uma API de E-commerce desenvolvida com Django Rest Framework. Ela permite o cadastro de clientes, listagem de produtos, criação e compra de produtos, além de gerenciar transações financeiras (saldo) dos clientes. A API também inclui autenticação JWT para proteger as rotas e segue a documentação OpenAPI (Swagger).

## Funcionalidades Principais

- Cadastro de clientes
- Verificação de e-mail
- Autenticação JWT
- Adicionar saldo ao cliente
- Criar produtos
- Listar produtos (público)
- Comprar produtos
- Listar transações
- Realizar logout
- Mudar senha do cliente
- Deletar perfil do cliente

## Tecnologias Utilizadas

- **Django** - Framework principal
- **Django Rest Framework (DRF)** - Para criação de APIs RESTful
- **drf-yasg** - Para geração de documentação Swagger/OpenAPI
- **JWT (JSON Web Tokens)** - Para autenticação
- **SQLite** (padrão) - Banco de dados
- **pipenv** - Para gerenciamento de dependências e ambiente virtual

## Configuração Inicial

### Pré-requisitos

- **Python 3.11 ou superior** - Certifique-se de que o Python está instalado corretamente.
- **pipenv** - Para criar um ambiente virtual e instalar dependências.

```bash
pip install pipenv
```

### Clonar o Repositório

```bash
git clone https://github.com/felipesantos9/Django_API_RESTful.git
cd Django_API_RESTful/backend
```

### Criar Ambiente Virtual
Utilize o **pipenv** para criar e ativar o ambiente virtual:
```bash
pipenv install
pipenv shell
```

### Instalar Dependências
Todas as dependências necessárias estão listadas no arquivo *Pipfile*. Após ativar o ambiente, instale as dependências:
```bash
pipenv install
```

### Configurar o Banco de Dados
Execute as migrações do Django para configurar o banco de dados:
```bash
python manage.py migrate
```

### Executar o Servidor
Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```
A API estará disponível em http://127.0.0.1:8000/

## Endpoints

### Autenticação e Cadastro

- `POST /api/register/`: Cadastro de novos clientes.
- `POST /api/verify-email/`: Verificação de e-mail (envia um código de verificação).
- `POST /api/login/`: Autenticação e geração de token JWT.
- `POST /api/logout/`: Logout com blacklist do token JWT.
- `POST /api/alterar-senha/`: Alterar a senha do usuário logado.
- `DELETE /api/delete-user/`: Apagar o usuário logado.

### Gestão de Produtos

- `POST /api/criar-produto/`: Cadastro de novos produtos.
- `POST /api/add-saldo/`: 
Adição de saldo para o usuário.
- `GET /api/produtos/`: Listar, filtrar e ordenar proodutos
- `POST /api/compra/`: Comprar produtos.
- `POST /api/transacoes/`: Listar, filtrar e ordenar transações (compras)

## Documentação Open API
A documentação da API está disponível em formato Swagger/OpenAPI:

- `http://127.0.0.1:8000/swagger/` <br>Interface interativa Swagger
- `http://127.0.0.1:8000/redoc/` <br> Interface Redoc

## Testes
Para rodar os testes automatizados:
```bash
python manage.py test
```

## Autenticação JWT
A API utiliza autenticação JWT para proteger as rotas. Após o login, um token JWT é gerado. Você precisa passar este token no cabeçalho Authorization em todas as requisições autenticadas.
```bash
Authorization: Bearer <seu_token>
```

## Exemplo de Uso
O arquivo `basic_client.py` na pasta `client` demonstra como interagir com a API.