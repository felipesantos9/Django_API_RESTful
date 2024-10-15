from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from .models import Produto, Cliente, Transacao, EmailVerification
import random
from django.core.mail import send_mail

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Verifica se o username já está em uso
        if User.objects.filter(username=validated_data['username']).exists():
            raise ValidationError("Este username já está em uso. Escolha outro.")
        
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        # Criar o perfil de verificação de e-mail
        verification_code = str(random.randint(100000, 999999))  # Gera um código de 6 dígitos
        EmailVerification.objects.create(user=user, verification_code=verification_code)

        # Enviar e-mail
        self.send_verification_email(user.email, verification_code)

        # Criação automática do perfil Cliente
        Cliente.objects.create(user=user)

        return user

    def send_verification_email(self, email, code):
        subject = "Código de Verificação"
        message = f"Seu código de verificação é: {code}"
        send_mail(subject, message, 'seu_email@gmail.com', [email])  # Use seu e-mail aqui