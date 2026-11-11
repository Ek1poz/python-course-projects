import factory
from factory.django import DjangoModelFactory

from my_app.models import Book, Category, CustomUser, Order, OrderItem


class UserFactory(DjangoModelFactory):
    """
    Create test users with a usable password.
    """

    class Meta:
        model = CustomUser
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda user: f'{user.username}@example.com')

    @factory.post_generation
    def password(
        user: CustomUser, create: bool, extracted: str | None, **_kwargs
    ):
        if create:
            user.set_password(extracted or 'TestPass123!')
            user.save(update_fields=['password'])


class CategoryFactory(DjangoModelFactory):
    """
    Create book categories for tests.
    """

    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{n}')


class BookFactory(DjangoModelFactory):
    """
    Create books with sensible defaults.
    """

    class Meta:
        model = Book

    category = factory.SubFactory(CategoryFactory)
    title = factory.Sequence(lambda n: f'Book {n}')
    author = 'A. Writer'
    price = '19.99'
    description = 'A sample book description.'
    stock = 10


class OrderFactory(DjangoModelFactory):
    """
    Create orders for checkout tests.
    """

    class Meta:
        model = Order

    first_name = 'Test'
    last_name = 'Customer'
    email = factory.Sequence(lambda n: f'customer{n}@example.com')


class OrderItemFactory(DjangoModelFactory):
    """
    Create order items for total-cost tests.
    """

    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    price = factory.LazyAttribute(lambda item: item.book.price)
    quantity = 1
