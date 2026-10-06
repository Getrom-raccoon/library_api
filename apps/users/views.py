import random
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    VerifyEmailSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifySerializer,
)


class PasswordResetRequestView(generics.GenericAPIView):
    """Запрос на сброс пароля: отправляет код на email"""
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Не говорим, что пользователя нет — защита от перебора
            return Response(
                {'message': 'Если такой email есть — код отправлен'},
                status=status.HTTP_200_OK,
            )

        # Генерируем код
        code = f"{random.randint(0, 999999):06d}"
        user.reset_code = code
        user.reset_code_created = timezone.now()
        user.save()

        send_mail(
            subject='Сброс пароля',
            message=f'Ваш код для сброса пароля: {code}\nОн действует 10 минут.',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Код отправлен на почту'}, status=status.HTTP_200_OK)


class PasswordResetVerifyView(generics.GenericAPIView):
    """Проверка кода и установка нового пароля"""
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        # Проверка срока (10 минут)
        if not user.reset_code_created or timezone.now() - user.reset_code_created > timedelta(minutes=10):
            return Response({'error': 'Код истёк, запросите новый'}, status=400)

        # Проверка кода
        if user.reset_code != code:
            return Response({'error': 'Неверный код'}, status=400)

        # Обновляем пароль
        user.set_password(new_password)
        user.reset_code = None
        user.reset_code_created = None
        user.save()

        return Response({'message': 'Пароль успешно изменён'}, status=200)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Проверка: если пользователь с таким email уже есть, но неактивен — перезаписываем код
        email = serializer.validated_data['email']
        existing = User.objects.filter(email=email).first()
        if existing and existing.is_active:
            return Response(
                {'error': 'Пользователь с такой почтой уже зарегистрирован'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Генерируем 6-значный код
        code = f"{random.randint(0, 999999):06d}"

        # Сохраняем пользователя (неактивного)
        if existing:
            existing.set_password(serializer.validated_data['password'])
            existing.email_code = code
            existing.email_code_created = timezone.now()
            existing.save()
        else:
            user = serializer.save(is_active=False)
            user.email_code = code
            user.email_code_created = timezone.now()
            user.save()

        # Отправляем письмо
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код: {code}\nОн действует 10 минут.',
            from_email=None,  # берётся из DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({'message': 'Код отправлен на почту'}, status=status.HTTP_200_OK)


class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'error': 'Email и код обязательны'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        # Проверка срока действия (10 минут)
        if not user.email_code_created or timezone.now() - user.email_code_created > timedelta(minutes=10):
            return Response({'error': 'Код истёк, запросите новый'}, status=400)

        # Проверка кода
        if user.email_code != code:
            return Response({'error': 'Неверный код'}, status=400)

        # Активация
        user.is_active = True
        user.email_code = None
        user.email_code_created = None
        user.save()

        # Возвращаем JWT-токены
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user