import requests

BASE_URL = "http://localhost:8000/api/"


class EcommerceClient:
    def __init__(self):
        self.token = None
        self.refresh = None

    def register(self, username, email, password):
        url = BASE_URL + "register/"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Usuário cadastrado com sucesso!")
        else:
            print(f"Erro no cadastro: {response.json()}")
    
    def verify_email(self, email, code):
        url = BASE_URL + "verify-email/"
        data = {
            "email": email,
            "code": code
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("E-mail verificado com sucesso!")
        else:
            print(f"Erro na verificação: {response.json()}")

    def login(self, username, password):
        url = BASE_URL + "login/"
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            self.token = response.json()['access']
            self.refresh = response.json()['refresh']
            print("Login realizado com sucesso! Tokens obtidos.")
        else:
            print(f"Erro no login: {response.json()}")

    def add_saldo(self, saldo):
        url = BASE_URL + "add-saldo/"
        headers = self._get_auth_headers()
        data = {"saldo": saldo}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"Saldo atualizado: {response.json()['message']}")
        else:
            print(f"Erro ao adicionar saldo: {response.json()}")

    def criar_produto(self, nome, preco, estoque):
        url = BASE_URL + "criar-produto/"
        headers = self._get_auth_headers()
        data = {
            "nome": nome,
            "preco": preco,
            "estoque": estoque
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Produto criado: {response.json()}")
        else:
            print(f"Erro ao criar produto: {response.json()}")

    def listar_produtos(self):
        url = BASE_URL + "produtos/"
        
        # Solicitar os parâmetros de busca, filtro e ordenação ao usuário
        pagina = input("Informe o número da página (default 1): ") or "1"
        itens_por_pagina = input("Informe o número de itens por página (default 10): ") or "10"
        nome = input("Informe o nome do produto para busca (opcional): ")
        preco_max = input("Informe o preço máximo (opcional): ")
        ordenar_por = input("Ordenar por (opções: 'estoque', 'preco', opcional): ")
        
        # Monta os parâmetros da URL
        params = {
            "pagina": pagina,
            "itens_por_pagina": itens_por_pagina,
            "nome": nome,
            "preco_max": preco_max,
            "ordenar_por": ordenar_por
        }

        # Remove os parâmetros vazios
        params = {k: v for k, v in params.items() if v}

        # Faz a requisição GET com os parâmetros
        response = requests.get(url, params=params)
        print(response.json())
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de produtos: {data['total_items']}")
            print(f"Página: {data['pagina']}, Itens por página: {data['itens_por_pagina']}")
            
            # Lista os produtos retornados
            for produto in data['produtos']:
                print(f"ID: {produto['id']}, Nome: {produto['nome']}, Preço: {produto['preco']}, Estoque: {produto['estoque']}")
        else:
            print(f"Erro ao listar produtos: {response.status_code} - {response.json()}")

    def comprar_produto(self, username, produto_id, quantidade):
        url = BASE_URL + "compra/"
        headers = self._get_auth_headers()
        data = {
            "username": username,
            "produto_id": produto_id,
            "quantidade": quantidade
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print("Compra realizada com sucesso!")
        else:
            print(f"Erro ao realizar compra: {response.json()}")

    def delete_user(self):
        url = BASE_URL + "delete-user/"
        headers = self._get_auth_headers()
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            print("Usuário deletado com sucesso.")
        else:
            print(f"Erro ao deletar o usuário: {response.json()}")

    def logout(self):
        url = BASE_URL + "logout/"
        headers = self._get_auth_headers()
        refresh_token = self.refresh
        data = {"refresh": refresh_token}
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            print("Logout realizado com sucesso.")
        else:
            print(f"Erro ao fazer logout: {response.json()}")

    def alterar_senha(self):
        url = BASE_URL + "alterar-senha/"
        headers = self._get_auth_headers()

        senha_atual = input("Digite sua senha atual: ")
        nova_senha = input("Digite sua nova senha: ")
        confirmar_senha = input("Confirme sua nova senha: ")

        data = {
            "senha_atual": senha_atual,
            "nova_senha": nova_senha,
            "confirmar_senha": confirmar_senha
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print("Senha alterada com sucesso!")
        else:
            print(f"Erro ao alterar a senha: {response.json()}")


    def _get_auth_headers(self):
        if not self.token:
            raise Exception("Usuário não autenticado. Faça login primeiro.")
        return {
            "Authorization": f"Bearer {self.token}"
        }


if __name__ == "__main__":
    client = EcommerceClient()

    # cadastro
    #print("### Cadastro de usuário ###")
    #client.register(username="felipe_santos", email="felipessantos2004@gmail.com", password="senha123")

    # Verifica o e-mail com o código fornecido
    #codigo_recebido = str(input("Informe o código de verificação recebido por e-mail: "))
    #client.verify_email(email="felipessantos2004@gmail.com", code=codigo_recebido)
    
    # login
    #print("\n### Login de usuário ###")
    #client.login(username="felipe_santos", password="senha123")

    # adicionar saldo
    #print("\n### Adicionar saldo ###")
    #client.add_saldo(100.00)

    # criar um novo produto
    #print("\n### Criar produto ###")
    #client.criar_produto(nome="Produto B", preco=40.00, estoque=20)

    #client.listar_produtos()

    # Testar realizar compra
    #print("\n### Realizar compra ###")
    #client.comprar_produto(username="felipe_santos", produto_id=1, quantidade=2)

    # Deletar usuário
    ###client.delete_user()

    # Logout
    #client.logout()

    # Alterar Senha
    #client.alterar_senha()
