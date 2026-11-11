from django.urls import path

from . import views
from .views import (
    BookListView,
    BookDetailView,
    BookCreateView,
    BookDeleteView,
    BookUpdateView,
    UserLoginView,
    UserLogoutView,
    RegisterView)

app_name = 'books'

urlpatterns = [
    path("category_report/", views.category_report_async, name="category_report"),
    path("books_report/", views.books_report_async, name="books_report"),
    path("async/<int:pk>/", views.book_detail_async, name="async_book_detail"),
    path("", BookListView.as_view(), name="book_list"),
    path("<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("add/", BookCreateView.as_view(), name="book_create"),
    path("<int:pk>/update/", BookUpdateView.as_view(), name="book_update"),
    path("<int:pk>/delete/", BookDeleteView.as_view(), name="book_delete"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("cart/add/<int:book_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:book_id>/", views.cart_remove, name="cart_remove"),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path(
        'payment/process/<int:order_id>/',
        views.payment_process,
        name='payment_process',
    ),
    path('payment/completed/', views.payment_completed, name='payment_completed'),
    path('payment/canceled/', views.payment_canceled, name='payment_canceled'),
    path('checkout/', views.order_create, name='order_create'),
]
