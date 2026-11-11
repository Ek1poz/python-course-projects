from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from my_app.models import Book, CustomUser, Order, OrderItem
from my_app.tests.factories import (
    BookFactory,
    CategoryFactory,
    OrderFactory,
    OrderItemFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


def add_permission(user: CustomUser, codename: str) -> CustomUser:
    """
    Give the test user one model permission.
    """
    user.user_permissions.add(Permission.objects.get(codename=codename))
    return user


def test_register(client) -> None:
    """
    Check that a visitor can register an account.
    """
    response = client.post(reverse('books:register'), {
        'username': 'flow-reader',
        'password1': 'SafePassword123!',
        'password2': 'SafePassword123!',
        'phone_number': '',
        'date_of_birth': '',
    })
    assert response.status_code == 302
    assert response['Location'] == reverse('books:login')
    assert CustomUser.objects.filter(username='flow-reader').exists()


def test_login(client) -> None:
    """
    Check that a registered user can log in.
    """
    user = UserFactory(username='flow-login')
    response = client.post(reverse('books:login'), {
        'username': user.username,
        'password': 'TestPass123!',
    })
    assert response.status_code == 302
    assert response['Location'] == reverse('books:book_list')


def test_create_book(client) -> None:
    """
    Check that an authorized user can create a book.
    """
    user = add_permission(UserFactory(), 'add_book')
    client.force_login(user)
    category = CategoryFactory()
    response = client.post(reverse('books:book_create'), {
        'category': category.pk,
        'title': 'Created in flow',
        'author': 'A. Writer',
        'price': '25.00',
        'description': 'Created through the form.',
        'stock': 4,
    })
    assert response.status_code == 302
    assert Book.objects.filter(title='Created in flow').exists()


def test_add_to_cart(client) -> None:
    """
    Check that adding a book puts it in the cart.
    """
    book = BookFactory()
    response = client.post(reverse('books:cart_add', args=[book.pk]))
    assert response.status_code == 302
    assert client.session['cart'][str(book.pk)]['quantity'] == 1
    response = client.get(reverse('books:cart_detail'))
    assert response.status_code == 200
    assert book.title.encode() in response.content


def test_update_cart_quantity(client) -> None:
    """
    Check that a shopper can update an item's quantity.
    """
    book = BookFactory()
    client.post(reverse('books:cart_add', args=[book.pk]))
    client.post(reverse('books:cart_add', args=[book.pk]), {
        'quantity': '3',
        'override': 'True',
    })
    assert client.session['cart'][str(book.pk)]['quantity'] == 3


def test_remove_from_cart(client) -> None:
    """
    Check that a shopper can remove a book from the cart.
    """
    book = BookFactory()
    client.post(reverse('books:cart_add', args=[book.pk]))
    response = client.post(reverse('books:cart_remove', args=[book.pk]))
    assert response.status_code == 302
    assert str(book.pk) not in client.session['cart']


def test_clear_cart(client) -> None:
    """
    Check that a shopper can clear the cart.
    """
    book = BookFactory()
    client.post(reverse('books:cart_add', args=[book.pk]))
    response = client.post(reverse('books:cart_clear'))
    assert response.status_code == 302
    assert 'cart' not in client.session


def test_checkout_page(client) -> None:
    """
    Check that a shopper can open the checkout page.
    """
    response = client.get(reverse('books:order_create'))
    assert response.status_code == 200
    assert b'Checkout' in response.content


def test_checkout(client) -> None:
    """
    Check that checkout creates an order and sends a confirmation.
    """
    book = BookFactory(price=Decimal('12.50'))
    client.post(reverse('books:cart_add', args=[book.pk]), {'quantity': '2'})
    with patch('my_app.views.send_mail') as send_mail:
        response = client.post(reverse('books:order_create'), {
            'first_name': 'Flow',
            'last_name': 'Customer',
            'email': 'flow@example.com',
        })
    order = Order.objects.get(email='flow@example.com')
    assert response.status_code == 302
    assert response['Location'] == reverse(
        'books:payment_process', args=[order.pk]
    )
    assert OrderItem.objects.get(order=order).get_cost() == Decimal('25.00')
    assert 'cart' not in client.session
    send_mail.assert_called_once()
    assert send_mail.call_args.kwargs['recipient_list'] == ['flow@example.com']


def test_stripe_checkout(client) -> None:
    """
    Check that payment checkout redirects to the mocked Stripe page.
    """
    order = OrderFactory()
    OrderItemFactory(order=order, price=Decimal('15.25'), quantity=2)
    with patch('my_app.views.stripe.checkout.Session.create') as create_session:
        create_session.return_value.url = 'https://stripe.example/checkout'
        response = client.post(
            reverse('books:payment_process', args=[order.pk])
        )
    assert response.status_code == 303
    assert response['Location'] == 'https://stripe.example/checkout'
    assert create_session.call_args.kwargs['line_items'][0][
        'price_data'
    ]['unit_amount'] == 3050


def test_payment_page(client) -> None:
    """
    Check that a shopper can open an order's payment page.
    """
    order = OrderFactory()
    OrderItemFactory(order=order)
    response = client.get(reverse('books:payment_process', args=[order.pk]))
    assert response.status_code == 200
    assert f'Order #{order.pk}'.encode() in response.content


def test_logout(client) -> None:
    """
    Check that a logged-in user can log out.
    """
    client.force_login(UserFactory())
    response = client.post(reverse('books:logout'))
    assert response.status_code == 302
    assert '_auth_user_id' not in client.session


def test_update_book(client) -> None:
    """
    Check that an authorized user can update a book.
    """
    user = add_permission(UserFactory(), 'change_book')
    client.force_login(user)
    book = BookFactory()
    response = client.post(reverse('books:book_update', args=[book.pk]), {
        'category': book.category_id,
        'title': 'Updated book title',
        'author': book.author,
        'price': '29.00',
        'description': book.description,
        'stock': 8,
    })
    book.refresh_from_db()
    assert response.status_code == 302
    assert book.title == 'Updated book title'


def test_delete_book(client) -> None:
    """
    Check that an authorized user can delete a book.
    """
    user = add_permission(UserFactory(), 'delete_book')
    client.force_login(user)
    book = BookFactory()
    response = client.post(reverse('books:book_delete', args=[book.pk]))
    assert response.status_code == 302
    assert not Book.objects.filter(pk=book.pk).exists()


def test_switch_to_ukrainian(client) -> None:
    """
    Check that the language switch selects Ukrainian.
    """
    response = client.post(reverse('set_language'), {
        'language': 'uk',
        'next': reverse('books:book_list'),
    })
    assert response.status_code == 302
    assert response.cookies['django_language'].value == 'uk'
    BookFactory()
    client.cookies['django_language'] = 'uk'
    response = client.get(reverse('books:book_list'))
    assert response.status_code == 200
    assert 'Список книг'.encode() in response.content
