from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Produto, Cliente, Transacao, EmailVerification
from .serializers import ProdutoSerializer, UserSerializer
from decimal import Decimal

# Cadastro de clientes
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuário cadastrado com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Adicionar saldo à conta do cliente
class AddSaldoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        saldo_adicionar = request.data.get('saldo')

        try:
            saldo_adicionar = Decimal(saldo_adicionar)  
        except (ValueError, TypeError):
            return Response({"error": "O valor do saldo deve ser numérico."}, status=status.HTTP_400_BAD_REQUEST)

        cliente.saldo += saldo_adicionar  
        cliente.save()

        return Response({"message": f"Saldo atualizado para {cliente.saldo}."}, status=status.HTTP_200_OK)

# Criar um novo produto
class CreateProdutoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProdutoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListarProdutosView(APIView):
    def get(self, request):
        produtos = Produto.objects.all()  # Pega todos os produtos
        serializer = ProdutoSerializer(produtos, many=True)  # Serializa os produtos
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Realizar uma compra
class CompraView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        username = request.data.get('username')
        produto_id = request.data.get('produto_id')
        quantidade = request.data.get('quantidade')

        try:
            user = User.objects.get(username=username)  
            cliente = Cliente.objects.get(user=user)
            produto = Produto.objects.get(id=produto_id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Produto.DoesNotExist:
            return Response({"error": "Produto não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        total = produto.preco * quantidade

        if cliente.saldo < total:
            return Response({"error": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST)

        if produto.estoque < quantidade:
            return Response({"error": "Estoque insuficiente"}, status=status.HTTP_400_BAD_REQUEST)

        # Realizar a transação
        cliente.saldo -= total
        produto.estoque -= quantidade
        cliente.save()
        produto.save()

        transacao = Transacao(cliente=cliente, produto=produto, quantidade=quantidade, total=total)
        transacao.save()

        return Response({"message": "Compra realizada com sucesso"}, status=status.HTTP_201_CREATED)
    
class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        try:
            verification = EmailVerification.objects.get(user__email=email)
        except EmailVerification.DoesNotExist:
            return Response({"error": "Código de verificação inválido."}, status=status.HTTP_404_NOT_FOUND)

        if verification.verification_code == code and not verification.is_verified:
            verification.is_verified = True
            verification.save()
            return Response({"message": "E-mail verificado com sucesso!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Código de verificação inválido ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user  # O usuário logado que faz a requisição

        try:
            # Deletar o perfil do cliente associado
            cliente = Cliente.objects.get(user=user)
            cliente.delete()

            # Deletar o registro de verificação de e-mail associado
            email_verification = EmailVerification.objects.get(user=user)
            email_verification.delete()

            # Deletar o próprio usuário
            user.delete()

            return Response({"message": "Usuário deletado com sucesso."}, status=status.HTTP_200_OK)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except EmailVerification.DoesNotExist:
            # Caso o registro de EmailVerification não exista, continuar a deleção do usuário
            user.delete()
            return Response({"message": "Usuário deletado sem registro de verificação de e-mail."}, status=status.HTTP_200_OK)
        

class LogoutView(APIView):
    def post(self, request):
        try:
            # Pega o token de refresh do body da requisição
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Adiciona o token na lista de bloqueio

            return Response({"message": "Logout realizado com sucesso!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)