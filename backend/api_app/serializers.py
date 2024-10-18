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
        if User.objects.filter(username=validated_data['username']).exists():
            raise ValidationError("Este username já está em uso. Escolha outro.")
        
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        verification_code = str(random.randint(100000, 999999)) 
        EmailVerification.objects.create(user=user, verification_code=verification_code)

        self.send_verification_email(user.email, verification_code)

        Cliente.objects.create(user=user)

        return user

    def send_verification_email(self, email, code):
        subject = "Código de Verificação"
        message = f"Seu código de verificação é: {code}"
        send_mail(subject, message, 'djangoapirestful@gmail.com', [email])  