from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Cliente, Produto, Transacao, EmailVerification
from decimal import Decimal

class RegisterViewTest(APITestCase):
    def test_register_and_verify_user(self):
        url = reverse('register')
        data = {
            'username': 'cliente1',
            'email': 'cliente1@email.com',
            'password': 'senha123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Usuário cadastrado com sucesso!')

        verification = EmailVerification.objects.get(user__email=data['email'])

        verify_url = reverse('verify_email')
        verify_data = {
            'email': data['email'],
            'code': verification.verification_code
        }
        verify_response = self.client.post(verify_url, verify_data, format='json')
        self.assertEqual(verify_response.status_code, 200)

        self.user = User.objects.get(username='cliente1')
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.assertIsNotNone(access_token)


class AddSaldoViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente2',
            'email': 'cliente2@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        self.cliente = Cliente.objects.create(user=self.user, saldo=Decimal('0.00'))
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_adicionar_saldo(self):
        url = reverse('add_saldo')
        data = {'saldo': '100.00'}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.cliente.refresh_from_db()
        self.assertEqual(str(self.cliente.saldo), '100.00')


class CreateProdutoViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente3',
            'email': 'cliente3@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_criar_produto(self):
        url = reverse('criar_produto')
        data = {
            'nome': 'Produto A',
            'preco': '150.00',
            'estoque': 20
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['nome'], 'Produto A')


class ListarProdutosViewTest(APITestCase):
    def setUp(self):
        Produto.objects.create(nome='Produto A', preco=Decimal('100.00'), estoque=10)
        Produto.objects.create(nome='Produto B', preco=Decimal('200.00'), estoque=5)

    def test_listar_produtos(self):
        url = reverse('listar_produtos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_items'], 2)

    def test_listar_produtos_com_filtro(self):
        url = reverse('listar_produtos') + '?preco_max=150'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['produtos']), 1)


class CompraViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente4',
            'email': 'cliente4@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        self.cliente = Cliente.objects.create(user=self.user, saldo=Decimal('500.00'))
        self.produto = Produto.objects.create(nome='Produto A', preco=Decimal('100.00'), estoque=5)
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_comprar_produto(self):
        url = reverse('compra')
        data = {
            'username': 'cliente4',
            'produto_id': self.produto.id,
            'quantidade': 3
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.produto.refresh_from_db()
        self.cliente.refresh_from_db()
        self.assertEqual(self.produto.estoque, 2)
        self.assertEqual(str(self.cliente.saldo), '200.00')



class LogoutViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente6',
            'email': 'cliente6@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def test_logout(self):
        url = reverse('logout')
        data = {'refresh': self.refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Logout realizado com sucesso!')


class ListarTransacoesViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente8',
            'email': 'cliente8@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        self.cliente = Cliente.objects.create(user=self.user, saldo=Decimal('500.00'))
        self.produto = Produto.objects.create(nome='Produto A', preco=Decimal('100.00'), estoque=10)
        self.transacao = Transacao.objects.create(cliente=self.cliente, produto=self.produto, quantidade=2, total=Decimal('200.00'))

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_listar_transacoes(self):
        url = reverse('listar_transacoes')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_items'], 1)

    def test_listar_transacoes_com_filtro(self):
        url = reverse('listar_transacoes') + '?produto=Produto A&quantidade_min=1'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_items'], 1)


class ChangePasswordViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente9',
            'email': 'cliente9@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_alterar_senha(self):
        url = reverse('alterar_senha')
        data = {
            'senha_atual': 'senha123',
            'nova_senha': 'novaSenha123',
            'confirmar_senha': 'novaSenha123'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Senha alterada com sucesso!')
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.check_password('novaSenha123'))


class DeleteUserViewTest(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'cliente10',
            'email': 'cliente10@email.com',
            'password': 'senha123'
        }
        self.user = User.objects.create_user(**self.user_data)

        self.cliente = Cliente.objects.create(user=self.user, saldo=Decimal('0.00'))

        verification = EmailVerification.objects.create(user=self.user, verification_code='123456')
        self.client.post(reverse('verify_email'), {'email': self.user_data['email'], 'code': verification.verification_code})

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_deletar_usuario(self):
        url = reverse('delete_user') 
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        self.assertIsNotNone(Cliente.objects.filter(user=self.user).first(), "Cliente não encontrado antes da deleção.")

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Usuário deletado com sucesso.')

        with self.assertRaises(Cliente.DoesNotExist):
            Cliente.objects.get(user=self.user)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.user_data['username'])
