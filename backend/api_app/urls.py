from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, AddSaldoView, CreateProdutoView, CompraView, VerifyEmailView, DeleteUserView, ListarProdutosView, LogoutView, ChangePasswordView, ListarTransacoesView

urlpatterns = [
    #cadastro de cliente
    path('register/', RegisterView.as_view(), name='register'),

    #autenticação 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #adicionar saldo 
    path('add-saldo/', AddSaldoView.as_view(), name='add_saldo'),

    #criar um novo produto
    path('criar-produto/', CreateProdutoView.as_view(), name='criar_produto'),
    
    #listar Produtos
    path('produtos/', ListarProdutosView.as_view(), name='listar_produtos'),

    #comprar produtos
    path('compra/', CompraView.as_view(), name='compra'),

    #Validar email
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),

    #apagar usuário
    path('delete-user/', DeleteUserView.as_view(), name='delete_user'),

    #Logout do usuário
    path('logout/', LogoutView.as_view(), name='logout'),

    #alterar Senha do usuário
    path('alterar-senha/', ChangePasswordView.as_view(), name='alterar_senha'),

    #Listar transacoes
    path('transacoes/', ListarTransacoesView.as_view(), name='listar_transacoes'),
]