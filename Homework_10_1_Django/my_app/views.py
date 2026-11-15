"""HTTP views for the bookstore catalog, cart, and checkout workflows."""

import logging

import stripe
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, F, Model, Q, QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .cart import Cart
from .forms import CustomUserCreationForm
from .models import Book, Category, Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


async def category_report_async(request: HttpRequest) -> HttpResponse:
    """Render a report containing each category and its book count.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response rendering the category report template.

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
    """Render the report of low-stock or high-priced books.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response rendering the books report template. Each listed book
        includes its calculated total stock value.

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
    """Render one book's details using an asynchronous database lookup.

    Args:
        request: The incoming HTTP request.
        pk: The primary key of the book to display.

    Returns:
        An HTTP response rendering the book detail template.

    Raises:
        Http404: If no book exists with the supplied primary key.

    """
    try:
        book = await Book.objects.select_related('category').aget(pk=pk)
    except Book.DoesNotExist as error:
        raise Http404(_('Book not found.')) from error
    return render(request, 'books/book_detail.html', {
        'book': book
    })


class BookListView(ListView):
    """Display a paginated, optionally title-filtered list of books.

    Django dispatches each request to this view and renders the configured
    book-list template. The ``q`` query parameter filters titles, and results
    are paginated in groups of five.

    Args:
        request: The incoming HTTP request, including an optional ``q``
            query parameter.

    Returns:
        An HTTP response rendering the book list and pagination controls.

    """

    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Model, Model]:
        """Return books ordered by primary key and filtered by the search term.

        Returns:
            A queryset of books, filtered by the ``q`` query parameter when
            that parameter is present.

        """
        queryset = super().get_queryset().order_by('pk')
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset


class BookDetailView(DetailView):
    """Display the details of the book identified by its primary key.

    Args:
        request: The incoming HTTP request.
        pk: The primary key supplied by the URL pattern.

    Returns:
        An HTTP response rendering the book detail template.

    """

    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Provide an authorized user with a form to create a book.

    A user must be authenticated and have the ``my_app.add_book`` permission.
    Django renders a form on GET and redirects to the book list after a
    successful submission.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response containing the form or the post-submission redirect.

    """

    model = Book
    template_name = 'books/book_form.html'
    fields = ('category', 'title', 'author', 'price', 'description', 'stock')
    success_url = reverse_lazy('books:book_list')
    permission_required = 'my_app.add_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Provide an authorized user with a form to update an existing book.

    A user must be authenticated and have the ``my_app.change_book``
    permission. The book is selected by the primary key in the URL.

    Args:
        request: The incoming HTTP request.
        pk: The primary key of the book to update.

    Returns:
        An HTTP response containing the form or the post-submission redirect.

    """

    model = Book
    template_name = 'books/book_form.html'
    fields = ('category', 'title', 'author', 'price', 'description', 'stock')
    permission_required = 'my_app.change_book'

    def get_success_url(self) -> str:
        """Return the detail page URL for the updated book.

        Returns:
            The URL of the detail page for the book just updated.

        """
        return reverse_lazy('books:book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Ask an authorized user to confirm deletion of a book.

    A user must be authenticated and have the ``my_app.delete_book``
    permission. The book is selected by the primary key in the URL.

    Args:
        request: The incoming HTTP request.
        pk: The primary key of the book to delete.

    Returns:
        An HTTP response showing the confirmation page or redirecting to the
        book list after deletion.

    """

    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
    permission_required = 'my_app.delete_book'


class RegisterView(CreateView):
    """Provide a form for creating a user account.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response containing the registration form or redirecting to
        the login page after successful registration.

    """

    form_class = CustomUserCreationForm
    template_name = 'books/register.html'
    success_url = reverse_lazy('books:login')


class UserLoginView(LoginView):
    """Provide a login form and authenticate submitted credentials.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response containing the login form or redirecting a
        successfully authenticated user to the book list.

    """

    template_name = 'books/login.html'

    def get_success_url(self) -> str:
        """Return the URL to visit after a successful login.

        Returns:
            The URL of the book list page.

        """
        return str(reverse_lazy('books:book_list'))


class UserLogoutView(LogoutView):
    """Log out the current user and redirect to the book list.

    Args:
        request: The incoming HTTP request from the authenticated user.

    Returns:
        An HTTP redirect response to the book list.

    """

    next_page = reverse_lazy("books:book_list")


def cart_detail(request: HttpRequest) -> HttpResponse:
    """Render the current session cart and its items.

    Args:
        request: The incoming HTTP request, whose session stores the cart.

    Returns:
        An HTTP response rendering the cart detail template.

    """
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@require_http_methods(["GET", "POST"])
def order_create(request: HttpRequest) -> HttpResponse:
    """Display checkout or create an order from the submitted cart.

    A GET request displays the checkout form. A valid POST creates an order
    and its items atomically, clears the cart, sends an order confirmation,
    and redirects to payment processing. Invalid cart data or order details
    produce a bad-request response.

    Args:
        request: The incoming HTTP request. POST requests provide the
            customer's first name, last name, and email address.

    Returns:
        An HTTP response rendering checkout, reporting invalid input, or
        redirecting to payment processing.

    """
    cart = Cart(request)
    if request.method == "POST":
        cart_data = cart.cart.copy()
        if not cart_data:
            return HttpResponseBadRequest(_("Your cart is empty."))

        try:
            quantities = {
                int(book_id): item["quantity"]
                for book_id, item in cart_data.items()
                if isinstance(item, dict)
            }
        except (KeyError, TypeError, ValueError):
            return HttpResponseBadRequest(_("Your cart contains invalid items."))

        if (
            len(quantities) != len(cart_data)
            or any(
                isinstance(quantity, bool)
                or not isinstance(quantity, int)
                or quantity < 1
                for quantity in quantities.values()
            )
        ):
            return HttpResponseBadRequest(_("Your cart contains invalid items."))

        books = Book.objects.in_bulk(quantities)
        if len(books) != len(quantities):
            return HttpResponseBadRequest(
                _("A book in your cart is no longer available.")
            )

        order = Order(
            first_name=request.POST.get("first_name", "").strip(),
            last_name=request.POST.get("last_name", "").strip(),
            email=request.POST.get("email", "").strip(),
        )
        try:
            order.full_clean()
        except ValidationError as error:
            return HttpResponseBadRequest(str(error))

        with transaction.atomic():
            order.save()
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        book=books[book_id],
                        price=books[book_id].price,
                        quantity=quantity,
                    )
                    for book_id, quantity in quantities.items()
                ]
            )
        cart.clear()
        send_mail(
            subject=_("Order received"),
            message=_(
                "We received your order. Its number is %(order_id)s."
            ) % {"order_id": order.pk},
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return redirect("books:payment_process", order_id=order.id)

    return render(request, "orders/create.html", {"cart": cart})


@require_http_methods(["GET", "POST"])
def payment_process(request: HttpRequest, order_id: int) -> HttpResponse:
    """Display payment details or create a Stripe Checkout session.

    A GET request displays the order's payment page. A valid POST creates a
    card-payment session with Stripe and redirects the customer to it.

    Args:
        request: The incoming HTTP request.
        order_id: The primary key of the order to pay.

    Returns:
        An HTTP response rendering the payment page, redirecting to Stripe,
        or reporting an invalid order total or payment-service failure.

    Raises:
        Http404: If no order exists with the supplied ID.

    """
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        items = list(order.items.select_related("book").all())
        total_cost = sum((item.get_cost() for item in items), start=0)
        if not items or total_cost <= 0:
            return HttpResponseBadRequest(
                _("An empty or zero-value order cannot be paid.")
            )

        success_url = request.build_absolute_uri(reverse("books:payment_completed"))
        cancel_url = request.build_absolute_uri(reverse("books:payment_canceled"))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {"name": f"Order {order.id}"},
                            "unit_amount": int(total_cost * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except stripe.StripeError:
            logger.exception(
                "Stripe Checkout session creation failed for order %s",
                order.pk,
            )
            return HttpResponse(
                _("The payment service is temporarily unavailable."),
                status=502,
            )
        return HttpResponse(status=303, headers={'Location': session.url})

    return render(request, 'orders/process.html', {
        'order': order
    })


def payment_completed(request: HttpRequest) -> HttpResponse:
    """Render the page shown after returning from successful payment.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response rendering the payment completion template.

    """
    return render(request, "orders/completed.html")


def payment_canceled(request: HttpRequest) -> HttpResponse:
    """Render the page shown after returning from canceled payment.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HTTP response rendering the payment cancellation template.

    """
    return render(request, "orders/canceled.html")


@require_POST
def cart_add(request: HttpRequest, book_id: int) -> HttpResponse:
    """Add a book to the session cart or set its quantity.

    This view accepts POST requests only. The optional ``quantity`` field
    defaults to one; setting ``override`` to ``True`` replaces the existing
    quantity instead of adding to it.

    Args:
        request: The incoming POST request, including quantity and override
            form values.
        book_id: The primary key of the book to add.

    Returns:
        An HTTP redirect to the cart, or a bad-request response if the
        quantity is not a positive integer.

    Raises:
        Http404: If no book exists with the supplied ID.

    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return HttpResponseBadRequest(_("Quantity must be a positive integer."))
    if quantity < 1:
        return HttpResponseBadRequest(_("Quantity must be a positive integer."))
    override = request.POST.get('override') == 'True'
    cart.add(book=book, quantity=quantity, override_quantity=override)

    return redirect('books:cart_detail')


@require_POST
def cart_remove(request: HttpRequest, book_id: int) -> HttpResponse:
    """Remove a book from the session cart.

    This view accepts POST requests only.

    Args:
        request: The incoming POST request, whose session stores the cart.
        book_id: The primary key of the book to remove.

    Returns:
        An HTTP redirect to the cart.

    Raises:
        Http404: If no book exists with the supplied ID.

    """
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect('books:cart_detail')


@require_POST
def cart_clear(request: HttpRequest) -> HttpResponse:
    """Remove all items from the session cart.

    This view accepts POST requests only.

    Args:
        request: The incoming POST request, whose session stores the cart.

    Returns:
        An HTTP redirect to the cart.

    """
    cart = Cart(request)
    cart.clear()
    return redirect('books:cart_detail')
