import stripe
from django.conf import settings
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, F, Q, QuerySet, Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .cart import Cart
from .models import Book, Category, Order, OrderItem
from .forms import CustomUserCreationForm

stripe.api_key = settings.STRIPE_SECRET_KEY


def category_report_view(request: HttpRequest) -> HttpResponse:
    """
    Handles the request to generate a statistical report for categories.

    Calculates the total number of books associated with each category
    using database annotation.
    """
    categories = Category.objects.annotate(
        books_count=Count('book')
    )

    return render(request, 'books/category_report.html', {
        'categories': categories,
    })


def books_report_view(request: HttpRequest) -> HttpResponse:
    """
    Handles the request to generate a report for specific books.

    Filters the database for books that are either low in stock (stock < 5)
    or expensive (price > 1000). It also calculates the total value of
    the remaining stock for these books.
    """
    books = Book.objects.annotate(
        total_value=F('price') * F('stock')
    ).filter(
        Q(stock__lt=5) | Q(price__gt=1000)
    ).select_related('category')

    return render(request, 'books/books_report.html', {
        'books': books,
    })


class BookListView(ListView):
    """
    Displays a paginated list of books.
    Includes basic search filtering by title.
    """
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Model, Model]:
        """Customizes the queryset to allow search filtering."""
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset


class BookDetailView(DetailView):
    """
    Displays detailed information for a single book.
    """
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Provides a form to create a new book.
    """
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']
    success_url = reverse_lazy('books:book_list')
    permission_required = 'my_app.add_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Provides a form to update an existing book.
    """
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']
    permission_required = 'my_app.change_book'

    def get_success_url(self) -> str:
        return reverse_lazy('books:book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Prompts the user to confirm the deletion of a book.
    """
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
    permission_required = 'my_app.delete_book'


class RegisterView(CreateView):
    """
    Provides a form to register a new user.
    """
    form_class = CustomUserCreationForm
    template_name = 'books/register.html'
    success_url = reverse_lazy('books:login')


class UserLoginView(LoginView):
    """
    Provides a form to log in a user.
    """
    template_name = 'books/login.html'

    def get_success_url(self) -> str:
        return str(reverse_lazy('books:book_list'))


class UserLogoutView(LogoutView):
    """
    Provides a form to log out a user.
    """
    next_page = reverse_lazy("books:book_list")


def order_create(request: HttpRequest) -> HttpResponse:
    """
    Handle order creation, process cart items, send confirmation email,
    and redirect to Stripe Checkout using an atomic database transaction.
    """
    cart = Cart(request)

    if request.method == "POST":
        first_name: str = request.POST.get("first_name", "")
        last_name: str = request.POST.get("last_name", "")
        email: str = request.POST.get("email", "")

        with transaction.atomic():
            order: Order = Order.objects.create(
                first_name=first_name, last_name=last_name, email=email
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item["book"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            cart.clear()

            send_mail(
                subject=f"Order #{order.id} Confirmation",
                message=f"Dear {order.first_name}, your order has been successfully placed.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=True,
            )

            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": f"Order {order.id}"},
                            "unit_amount": int(order.get_total_cost() * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri("/books/") + "?success=true",
                cancel_url=request.build_absolute_uri("/books/") + "?canceled=true",
            )
            return redirect(session.url, code=303)

    return render(request, 'orders/create.html', {'cart': cart})


@require_POST
def cart_add(request: HttpRequest, book_id: int) -> HttpResponse:
    """
    Add a selected book to the cart and redirect to check out.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.add(book=book, quantity=1)
    return redirect('books:order_create')

@require_POST
def cart_remove(request, book_id):
    """
    Remove a selected book from the cart.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect('books:order_create')

@require_POST
def cart_clear(request):
    """
    Clear the cart.
    """
    cart = Cart(request)
    cart.clear()
    return redirect('books:order_create')