from rest_framework import generics, status, viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import News, Category
from .serializers import NewsSerializer, CategorySerializer
from users.permissions import IsTeacher 

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

class NewsListView(generics.ListAPIView):
    queryset = News.objects.all().order_by('-publish_date')  # последние новости первыми
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Новости"],
        summary="Список всех новостей",
        description="Возвращает список всех опубликованных новостей.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class NewsCreateView(generics.GenericAPIView):
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    @extend_schema(
        tags=["Новости"],
        summary="Создание новости",
        description="Создаёт новость с указанной категорией. Категория создаётся, если не существует.",
        responses={
            201: OpenApiResponse(response=NewsSerializer, description="Новость создана"),
            400: OpenApiResponse(description="Некорректные данные"),
            403: OpenApiResponse(description="Доступ запрещен"),
        }
    )
    
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        category_input = data.get('category')

        if not category_input:
            return Response({"detail": "Поле 'category' обязательно."},
                            status=status.HTTP_400_BAD_REQUEST)

        category = None

        # Если category_input - число (или строка-число), проверяем как ID
        if str(category_input).isdigit():
            try:
                category = Category.objects.get(id=int(category_input))
            except Category.DoesNotExist:
                return Response({"detail": "Категория с таким ID не найдена."},
                                status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(category_input, str):
            category = Category.objects.filter(name__iexact=category_input.strip()).first()

            if not category:
                # Создаём новую категорию
                category = Category.objects.create(name=category_input.strip())

        else:
            return Response({"detail": "Некорректный формат поля 'category'."},
                            status=status.HTTP_400_BAD_REQUEST)

        data.pop('category')  # убираем из данных, чтобы не мешал сериализатору

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, category=category)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
