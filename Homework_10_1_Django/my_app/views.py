from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.db.models import F, Q, Count
from .models import Category, Book


def category_report_view(request : HttpRequest) -> HttpResponse:
    """
        Handles the request to generate a statistical report for categories.

        Calculates the total number of books associated with each category
        using database annotation.
    """
    categories = Category.objects.annotate(
        books_count = Count('book')
    )

    return render(request, 'category_report.html', {
        'categories': categories,
    })


def books_report_view(request : HttpRequest) -> HttpResponse:
    """
        Handles the request to generate a report for specific books.

        Filters the database for books that are either low in stock (stock < 5)
        or expensive (price > 1000). It also calculates the total value of
        the remaining stock for these books.
    """
    books = Book.objects.annotate(
        total_value = F('price') * F('stock')
    ).filter(
        Q(stock__lt = 5) | Q(price__gt = 1000)
    ).select_related('category')

    return render(request, 'books_report.html', {
        'books': books,
    })

