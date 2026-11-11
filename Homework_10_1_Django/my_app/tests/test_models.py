from decimal import Decimal

import pytest
from django.utils.translation import override

from my_app.tests.factories import (
    BookFactory,
    CategoryFactory,
    OrderFactory,
    OrderItemFactory,
)
from my_app.models import CustomUser


pytestmark = pytest.mark.django_db


def test_category_str() -> None:
    """
    Check that a category displays its name.
    """
    category = CategoryFactory(name='History')
    assert str(category) == 'History'


def test_book_str() -> None:
    """
    Check that a book displays its title and author.
    """
    book = BookFactory(title='Django', author='Ada')
    assert str(book) == 'Django (Ada)'


def test_user_str() -> None:
    """
    Check that a user displays their username.
    """
    user = CustomUser.objects.create_user(username='reader', password='pass')
    assert str(user) == 'reader'


def test_order_str() -> None:
    """
    Check that an order displays its ID.
    """
    order = OrderFactory()
    assert str(order) == f'Order {order.pk}'


def test_order_item_str() -> None:
    """
    Check that an order item displays its ID.
    """
    item = OrderItemFactory()
    assert str(item) == str(item.pk)


def test_order_item_cost() -> None:
    """
    Check that the item cost includes its quantity.
    """
    item = OrderItemFactory(price=Decimal('12.50'), quantity=3)
    assert item.get_cost() == Decimal('37.50')


def test_order_total() -> None:
    """
    Check that an order total includes all of its items.
    """
    order = OrderFactory()
    OrderItemFactory(order=order, price=Decimal('7.25'), quantity=2)
    OrderItemFactory(order=order, price=Decimal('3.50'), quantity=1)
    assert order.get_total_cost() == Decimal('18.00')


def test_model_label_ukrainian() -> None:
    """
    Check that model labels can be translated.
    """
    from my_app.models import Book

    with override('uk'):
        assert str(Book._meta.get_field('title').verbose_name) == 'назва'
