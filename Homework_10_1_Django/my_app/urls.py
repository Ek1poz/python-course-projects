from django.urls import path
from .views import category_report_view, books_report_view

urlpatterns = [
    path('category_report/', category_report_view, name='category_report'),
    path('books_report/', books_report_view, name='books_report'),
]