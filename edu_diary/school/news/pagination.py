from rest_framework.pagination import PageNumberPagination

class NewsPagination(PageNumberPagination):
    page_size = 6  # Количество новостей на странице
    page_size_query_param = 'page_size'
    max_page_size = 100
