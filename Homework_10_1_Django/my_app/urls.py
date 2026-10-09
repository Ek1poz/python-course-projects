from django.urls import path
from .views import (
    category_report_view,
    books_report_view,
    BookListView,
    BookDetailView,
    BookCreateView,
    BookDeleteView,
    BookUpdateView)

app_name = 'books'

urlpatterns = [
    path('category_report/', category_report_view, name='category_report'),
    path('books_report/', books_report_view, name='books_report'),
    path('', BookListView.as_view(), name='book_list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('add/', BookCreateView.as_view(), name='book_create'),
    path('<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
]
