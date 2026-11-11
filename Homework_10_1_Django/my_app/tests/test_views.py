from decimal import Decimal

import pytest
from django.urls import reverse

from my_app.tests.factories import BookFactory, CategoryFactory


pytestmark = pytest.mark.django_db


def test_book_list(client) -> None:
    """
    Check that the book list page displays books.
    """
    book = BookFactory(title='Visible book')
    response = client.get(reverse('books:book_list'))
    assert response.status_code == 200
    assert book.title.encode() in response.content


def test_book_search(client) -> None:
    """
    Check that search results match the requested title.
    """
    BookFactory(title='Python basics')
    BookFactory(title='Unrelated')
    response = client.get(reverse('books:book_list'), {'q': 'python'})
    assert len(response.context['books']) == 1
    assert response.context['books'][0].title == 'Python basics'


def test_async_book_detail(client) -> None:
    """
    Check that the async detail page displays an existing book.
    """
    book = BookFactory()
    response = client.get(reverse('books:async_book_detail', args=[book.pk]))
    assert response.status_code == 200
    assert response.context['book'].pk == book.pk


def test_async_category_report(client) -> None:
    """
    Check that the async category report counts its books.
    """
    category = CategoryFactory(name='Science')
    BookFactory(category=category)
    BookFactory(category=category)
    response = client.get(reverse('books:category_report'))
    assert response.status_code == 200
    assert response.context['categories'][0].books_count == 2


def test_async_books_report(client) -> None:
    """
    Check that the async report shows low-stock books and their value.
    """
    book = BookFactory(price=Decimal('10.00'), stock=2)
    BookFactory(price=Decimal('10.00'), stock=10)
    response = client.get(reverse('books:books_report'))
    assert response.status_code == 200
    assert [item.pk for item in response.context['books']] == [book.pk]
    assert response.context['books'][0].total_value == Decimal('20.00')


def test_book_create_login_required(client) -> None:
    """
    Check that an anonymous user is sent to the login page.
    """
    response = client.get(reverse('books:book_create'))
    assert response.status_code == 302
    assert reverse('books:login') in response['Location']


def test_registration_page(client) -> None:
    """
    Check that the registration page contains its form.
    """
    response = client.get(reverse('books:register'))
    assert response.status_code == 200
    assert 'form' in response.context
