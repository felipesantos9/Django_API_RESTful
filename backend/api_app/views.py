from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Produto, Cliente, Transacao, EmailVerification
from .serializers import ProdutoSerializer, UserSerializer, TransacaoSerializer
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



#cadastro de clientes
class RegisterView(APIView):
    @swagger_auto_schema(
        operation_summary="Registrar um novo usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="Nome de usuário"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email do usuário"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Senha do usuário"),
            },
            required=['username', 'email', 'password'],
        ),
        responses={
            201: openapi.Response('Usuário cadastrado com sucesso!'),
            400: openapi.Response('Erro na validação dos dados.'),
        }
    )


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Usuário cadastrado com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# verificar  email  
class VerifyEmailView(APIView):
    @swagger_auto_schema(
        operation_summary="Verificar o e-mail do usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email do usuário"),
                'code': openapi.Schema(type=openapi.TYPE_STRING, description="Código de verificação enviado ao e-mail"),
            },
            required=['email', 'code'],
        ),
        responses={
            200: openapi.Response('E-mail verificado com sucesso!'),
            404: openapi.Response('Código de verificação inválido.'),
            400: openapi.Response('Código de verificação inválido ou já utilizado.'),
        }
    )


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



#adicionar saldo a conta do cliente
class AddSaldoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Adicionar saldo à conta do cliente",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'saldo': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL, description="Valor a ser adicionado ao saldo"),
            },
            required=['saldo'],
        ),
        responses={
            200: openapi.Response('Saldo atualizado com sucesso.'),
            404: openapi.Response('Cliente não encontrado.'),
            400: openapi.Response('Erro ao adicionar saldo.'),
        }
    )


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


#criar um novo produto
class CreateProdutoView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Criar um novo produto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nome': openapi.Schema(type=openapi.TYPE_STRING, description="Nome do produto"),
                'preco': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL, description="Preço do produto"),
                'estoque': openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantidade em estoque"),
            },
            required=['nome', 'preco', 'estoque'],
        ),
        responses={
            201: openapi.Response('Produto criado com sucesso!'),
            400: openapi.Response('Erro na validação dos dados.'),
        }
    )


    def post(self, request):
        serializer = ProdutoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#listar produtos (publica)
class ListarProdutosView(ListAPIView):
    serializer_class = ProdutoSerializer

    @swagger_auto_schema(
        operation_summary="Listar todos os produtos",
        manual_parameters=[
            openapi.Parameter(
                'nome', openapi.IN_QUERY, description="Filtrar por nome do produto (contém)", 
                type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'preco_max', openapi.IN_QUERY, description="Filtrar por preço máximo", 
                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, required=False
            ),
            openapi.Parameter(
                'ordenar_por', openapi.IN_QUERY, description="Ordenar por 'estoque' ou 'preco'", 
                type=openapi.TYPE_STRING, enum=['estoque', 'preco'], required=False
            ),
            openapi.Parameter(
                'itens_por_pagina', openapi.IN_QUERY, description="Número de itens por página (padrão: 10)", 
                type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'pagina', openapi.IN_QUERY, description="Número da página (padrão: 1)", 
                type=openapi.TYPE_INTEGER, required=False
            ),
        ],
        responses={
            200: openapi.Response(
                'Lista de produtos retornada com sucesso.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_items': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número total de produtos'),
                        'pagina': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número da página atual'),
                        'itens_por_pagina': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número de itens por página'),
                        'produtos': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Produto individual')
                        ),
                    }
                )
            ),
        }
    )


    def get_queryset(self):
        
        queryset = Produto.objects.all()

        nome = self.request.query_params.get('nome', None)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        preco_max = self.request.query_params.get('preco_max', None)
        if preco_max:
            queryset = queryset.filter(preco__lte=preco_max)

        ordenar_por = self.request.query_params.get('ordenar_por', None)
        if ordenar_por in ['estoque', 'preco']:
            queryset = queryset.order_by(ordenar_por)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        page_size = int(request.query_params.get('itens_por_pagina', 10)) 
        page = int(request.query_params.get('pagina', 1))  
        total_items = queryset.count()  

        start = (page - 1) * page_size
        end = start + page_size
        produtos_paginados = queryset[start:end]

        serializer = ProdutoSerializer(produtos_paginados, many=True)

        return Response({
            "total_items": total_items,
            "pagina": page,
            "itens_por_pagina": page_size,
            "produtos": serializer.data
        }, status=status.HTTP_200_OK)
    
#realizar uma compra
class CompraView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Realizar uma compra",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="Nome de usuário do cliente"),
                'produto_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID do produto a ser comprado"),
                'quantidade': openapi.Schema(type=openapi.TYPE_INTEGER, description="Quantidade do produto"),
            },
            required=['username', 'produto_id', 'quantidade'],
        ),
        responses={
            201: openapi.Response('Compra realizada com sucesso.'),
            404: openapi.Response('Usuário, cliente ou produto não encontrado.'),
            400: openapi.Response('Saldo insuficiente ou estoque insuficiente.'),
        }
    )


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

        cliente.saldo -= total
        produto.estoque -= quantidade
        cliente.save()
        produto.save()

        transacao = Transacao(cliente=cliente, produto=produto, quantidade=quantidade, total=total)
        transacao.save()

        return Response({"message": "Compra realizada com sucesso"}, status=status.HTTP_201_CREATED)
    

#listar transacoes
class ListarTransacoesView(ListAPIView):
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Listar transações do cliente",
        manual_parameters=[
            openapi.Parameter(
                'produto', openapi.IN_QUERY, description="Filtrar por nome do produto (contém)", 
                type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                'quantidade_min', openapi.IN_QUERY, description="Filtrar por quantidade mínima", 
                type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'ordenar_por', openapi.IN_QUERY, description="Ordenar por 'data' ou 'total'", 
                type=openapi.TYPE_STRING, enum=['data', 'total'], required=False
            ),
            openapi.Parameter(
                'itens_por_pagina', openapi.IN_QUERY, description="Número de itens por página (padrão: 10)", 
                type=openapi.TYPE_INTEGER, required=False
            ),
            openapi.Parameter(
                'pagina', openapi.IN_QUERY, description="Número da página (padrão: 1)", 
                type=openapi.TYPE_INTEGER, required=False
            ),
        ],
        responses={
            200: openapi.Response(
                'Lista de transações retornada com sucesso.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_items': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número total de transações'),
                        'pagina': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número da página atual'),
                        'itens_por_pagina': openapi.Schema(type=openapi.TYPE_INTEGER, description='Número de itens por página'),
                        'transacoes': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_OBJECT, description='Transação individual')
                        ),
                    }
                )
            ),
            403: openapi.Response('Acesso negado.'),
        }
    )

    def get_queryset(self):
        cliente = self.request.user.cliente

        queryset = Transacao.objects.filter(cliente=cliente)

        nome_produto = self.request.query_params.get('produto', None)
        if nome_produto:
            queryset = queryset.filter(produto__nome__icontains=nome_produto)

        quantidade_min = self.request.query_params.get('quantidade_min', None)
        if quantidade_min:
            queryset = queryset.filter(quantidade__gte=quantidade_min)

        ordenar_por = self.request.query_params.get('ordenar_por', None)
        if ordenar_por in ['data', 'total']:
            queryset = queryset.order_by(ordenar_por)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page_size = int(request.query_params.get('itens_por_pagina', 10)) 
        page = int(request.query_params.get('pagina', 1)) 
        total_items = queryset.count()  

        start = (page - 1) * page_size
        end = start + page_size
        transacoes_paginadas = queryset[start:end]

        serializer = TransacaoSerializer(transacoes_paginadas, many=True)

        return Response({
            "total_items": total_items,
            "pagina": page,
            "itens_por_pagina": page_size,
            "transacoes": serializer.data
        }, status=status.HTTP_200_OK)
    

#mudar senha 
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Alterar a senha do usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'senha_atual': openapi.Schema(type=openapi.TYPE_STRING, description="Senha atual do usuário"),
                'nova_senha': openapi.Schema(type=openapi.TYPE_STRING, description="Nova senha do usuário"),
                'confirmar_senha': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmação da nova senha"),
            },
            required=['senha_atual', 'nova_senha', 'confirmar_senha'],
        ),
        responses={
            200: openapi.Response('Senha alterada com sucesso!'),
            400: openapi.Response('A senha atual está incorreta ou as senhas não correspondem.'),
        }
    )


    def post(self, request):
        user = request.user

        senha_atual = request.data.get('senha_atual')
        nova_senha = request.data.get('nova_senha')
        confirmar_senha = request.data.get('confirmar_senha')

        if not user.check_password(senha_atual):
            return Response({"error": "A senha atual está incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        if nova_senha != confirmar_senha:
            return Response({"error": "A nova senha e a confirmação não correspondem."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(nova_senha)
        user.save()

        return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)


#fazerlogout  
class LogoutView(APIView):
    @swagger_auto_schema(
        operation_summary="Logout do usuário",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Token de refresh do usuário"),
            },
            required=['refresh'],
        ),
        responses={
            200: openapi.Response('Logout realizado com sucesso!'),
            400: openapi.Response('Erro no logout.'),
        }
    )


    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  

            return Response({"message": "Logout realizado com sucesso!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    #deletar user       
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Deletar usuário",
        responses={
            200: openapi.Response('Usuário deletado com sucesso.'),
            404: openapi.Response('Cliente não encontrado.'),
        }
    )

    def delete(self, request):
        user = request.user  

        try:
            cliente = Cliente.objects.get(user=user)
            cliente.delete()

            email_verification = EmailVerification.objects.get(user=user)
            email_verification.delete()

            user.delete()

            return Response({"message": "Usuário deletado com sucesso."}, status=status.HTTP_200_OK)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except EmailVerification.DoesNotExist:
            user.delete()
            return Response({"message": "Usuário deletado sem registro de verificação de e-mail."}, status=status.HTTP_200_OK)