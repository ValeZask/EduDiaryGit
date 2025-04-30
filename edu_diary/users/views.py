from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .permissions import IsTeacher
from .custom_auth import CsrfExemptSessionAuthentication



from django.contrib.auth import get_user_model
from .models import Profile, StudentParent
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserUpdateSerializer, StudentParentSerializer
)
from .custom_auth import CsrfExemptSessionAuthentication

User = get_user_model()


@extend_schema(tags=["Аутентификация"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        summary="Регистрация нового пользователя",
        description="Создание нового пользователя с профилем",
        responses={
            201: OpenApiResponse(response=UserSerializer, description="Успешная регистрация"),
            400: OpenApiResponse(description="Ошибка валидации данных")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user)

        return Response(
            UserSerializer(user, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Аутентификация"])
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        summary="Авторизация пользователя",
        description="Авторизация пользователя по email и паролю",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Успешная авторизация"),
            400: OpenApiResponse(description="Некорректные учетные данные")
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Неверные учетные данные"},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=["Аутентификация"])
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        summary="Выход из системы",
        description="Завершение сессии пользователя",
        responses={
            200: OpenApiResponse(description="Успешный выход")
        }
    )
    def post(self, request):
        logout(request)
        return Response(
            {"detail": "Успешный выход из системы"},
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["Профиль"])
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        summary="Получение профиля",
        description="Получение профиля текущего пользователя",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Профиль пользователя")
        }
    )
    def get_object(self):
        return self.request.user


@extend_schema(tags=["Профиль"])
class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        summary="Обновление профиля",
        description="Обновление данных профиля текущего пользователя",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Обновленный профиль"),
            400: OpenApiResponse(description="Ошибка валидации данных")
        }
    )
    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(UserSerializer(instance).data)


@extend_schema(tags=["Связь Ученик-Родитель"])
class StudentParentListCreateView(generics.ListCreateAPIView):
    queryset = StudentParent.objects.all()
    serializer_class = StudentParentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'parent':
            return StudentParent.objects.filter(parent=user)
        return super().get_queryset()

    @extend_schema(
        summary="Получение списка связей ученик-родитель",
        description="Возвращает список связей. Родители видят только свои связи, учителя — все.",
        responses={
            200: OpenApiResponse(response=StudentParentSerializer(many=True), description="Список связей"),
            401: OpenApiResponse(description="Неавторизован")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создание связи ученик-родитель",
        description="Создает связь между учеником и родителем. Доступно только учителям.",
        responses={
            201: OpenApiResponse(response=StudentParentSerializer, description="Связь создана"),
            400: OpenApiResponse(description="Ошибка валидации"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    )
    def post(self, request, *args, **kwargs):
        if not request.user.role == 'teacher':
            return Response(
                {"detail": "Только учителя могут создавать связи"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


@extend_schema(tags=["Связь Ученик-Родитель"])
class StudentParentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentParent.objects.all()
    serializer_class = StudentParentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'parent':
            return StudentParent.objects.filter(parent=user)
        return super().get_queryset()

    @extend_schema(
        summary="Получение связи ученик-родитель",
        description="Воз  Возвращает данные конкретной связи. Родители видят только свои связи, учителя — все.",
        responses={
            200: OpenApiResponse(response=StudentParentSerializer, description="Данные связи"),
            401: OpenApiResponse(description="Неавторизован"),
            404: OpenApiResponse(description="Связь не найдена")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление связи ученик-родитель",
        description="Обновляет связь. Доступно только учителям.",
        responses={
            200: OpenApiResponse(response=StudentParentSerializer, description="Связь обновлена"),
            400: OpenApiResponse(description="Ошибка валидации"),
            403: OpenApiResponse(description="Доступ запрещен")
        }
    )
    def put(self, request, *args, **kwargs):
        if not request.user.role == 'teacher':
            return Response(
                {"detail": "Только учителя могут обновлять связи"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление связи ученик-родитель",
        description="Удаляет связь. Доступно только учителям.",
        responses={
            204: OpenApiResponse(description="Связь удалена"),
            403: OpenApiResponse(description="Доступ запрещен"),
            404: OpenApiResponse(description="Связь не найдена")
        }
    )
    def delete(self, request, *args, **kwargs):
        if not request.user.role == 'teacher':
            return Response(
                {"detail": "Только учителя могут удалять связи"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)