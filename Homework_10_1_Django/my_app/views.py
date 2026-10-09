from django.db.models import Count, F, Q, QuerySet, Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Book, Category


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
    """Displays detailed information for a single book."""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookCreateView(CreateView):
    """Provides a form to create a new book."""
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']
    success_url = reverse_lazy('books:book_list')


class BookUpdateView(UpdateView):
    """Provides a form to update an existing book."""
    model = Book
    template_name = 'books/book_form.html'
    fields = ['category', 'title', 'author', 'price', 'description', 'stock']

    def get_success_url(self) -> str:
        return reverse_lazy('books:book_detail', kwargs={'pk': self.object.pk})


class BookDeleteView(DeleteView):
    """Prompts the user to confirm the deletion of a book."""
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
