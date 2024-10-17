from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, AddSaldoView, CreateProdutoView, CompraView, VerifyEmailView, DeleteUserView, ListarProdutosView, LogoutView

urlpatterns = [
    # Rota de cadastro de cliente
    path('register/', RegisterView.as_view(), name='register'),

    # Autenticação com JWT
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Adicionar saldo ao cliente autenticado
    path('add-saldo/', AddSaldoView.as_view(), name='add_saldo'),

    # Criar um novo produto
    path('criar-produto/', CreateProdutoView.as_view(), name='criar_produto'),
    
    # Listar Produtos
    path('produtos/', ListarProdutosView.as_view(), name='listar_produtos'),

    # Rota de compra de produtos
    path('compra/', CompraView.as_view(), name='compra'),

    # Validar email
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),

    #Apagar usuário
    path('delete-user/', DeleteUserView.as_view(), name='delete_user'),

    #Logout do usuário
    path('logout/', LogoutView.as_view(), name='logout'),
]