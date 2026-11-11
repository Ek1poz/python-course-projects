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
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
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


async def category_report_async(request: HttpRequest) -> HttpResponse:
    """
    Render category statistics using Django's asynchronous ORM iterator.
    """
    categories = [
        category async for category in Category.objects.annotate(
            books_count=Count('book')
        ).aiterator()
    ]
    return render(request, 'books/category_report.html', {
        'categories': categories,
    })


async def books_report_async(request: HttpRequest) -> HttpResponse:
    """
    Render the low-stock and expensive-books report asynchronously.
    """
    queryset = Book.objects.annotate(
        total_value=F('price') * F('stock')
    ).filter(
        Q(stock__lt=5) | Q(price__gt=1000)
    ).select_related('category')
    books = [book async for book in queryset.aiterator()]
    return render(request, 'books/books_report.html', {
        'books': books
    })


async def book_detail_async(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Display a book using an asynchronous database lookup.
    """
    try:
        book = await Book.objects.select_related('category').aget(pk=pk)
    except Book.DoesNotExist as error:
        raise Http404(_('Book not found.')) from error
    return render(request, 'books/book_detail.html', {
        'book': book
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
        queryset = super().get_queryset().order_by('pk')
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


def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Render the cart detail page displaying all added items.
    """
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


def order_create(request: HttpRequest) -> HttpResponse:
    """
    Create an order from cart items, clear the cart, and redirect to payment processing.
    """
    cart = Cart(request)
    if request.method == "POST":
        with transaction.atomic():
            order = Order.objects.create(
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                email=request.POST.get("email"),
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
            subject=_('Order confirmation'),
            message=_('Thank you for your order. Your order number is %(order_id)s.')
            % {'order_id': order.pk},
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return redirect("books:payment_process", order_id=order.id)

    return render(request, "orders/create.html", {"cart": cart})


def payment_process(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Initiate a Stripe checkout session for the specified order.
    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("books:payment_completed"))
        cancel_url = request.build_absolute_uri(reverse("books:payment_canceled"))

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
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return HttpResponse(status=303, headers={'Location': session.url})

    return render(request, 'orders/process.html', {
        'order': order
    })


def payment_completed(request: HttpRequest) -> HttpResponse:
    """
    Render the successful payment completion page.
    """
    return render(request, "orders/completed.html")


def payment_canceled(request: HttpRequest) -> HttpResponse:
    """
    Render the payment cancellation page.
    """
    return render(request, "orders/canceled.html")


@require_POST
def cart_add(request: HttpRequest, book_id: int) -> HttpResponse:
    """
    Add a selected book to the cart or update its quantity.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get('override') == 'True'
    cart.add(book=book, quantity=quantity, override_quantity=override)

    return redirect('books:cart_detail')


@require_POST
def cart_remove(request, book_id):
    """
    Remove a selected book from the cart.
    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect('books:cart_detail')


@require_POST
def cart_clear(request):
    """
    Clear the cart.
    """
    cart = Cart(request)
    cart.clear()
    return redirect('books:cart_detail')
