from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils.translation import override

from my_app.models import Book, Category, CustomUser, Order, OrderItem


pytestmark = pytest.mark.django_db


def test_category_string_representation() -> None:
    """Show the category name in its string representation."""
    # Generated with AI, reviewed and modified
    category = Category.objects.create(name="History", slug="history")

    assert str(category) == "History"


def test_user_string_representation() -> None:
    """Show the username in its string representation."""
    # Generated with AI, reviewed and modified
    user = CustomUser.objects.create_user(username="reader", password="pass")

    assert str(user) == "reader"


def test_book_title_label_is_translated_to_ukrainian() -> None:
    """Translate the book title field label into Ukrainian."""
    # Generated with AI, reviewed and modified
    with override("uk"):
        assert str(Book._meta.get_field("title").verbose_name) == "назва"


class TestBookModel:
    """Test the Book model."""

    def setup_method(self) -> None:
        """Create a category for book tests."""
        self.category = Category.objects.create(
            name="Fiction",
            slug="fiction",
        )

    def test_create_book(self) -> None:
        """Create a book and verify its saved fields."""
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            category=self.category,
            title="The Example",
            author="A. Writer",
            price=Decimal("19.99"),
            description="A sample description.",
            stock=8,
        )

        assert book.pk is not None
        assert book.title == "The Example"
        assert book.author == "A. Writer"
        assert book.price == Decimal("19.99")
        assert book.category == self.category
        assert book.stock == 8

    def test_book_string_representation(self) -> None:
        """Show the book title and author."""
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            category=self.category,
            title="The Example",
            author="A. Writer",
            price=Decimal("19.99"),
            description="A sample description.",
            stock=8,
        )

        assert str(book) == "The Example (A. Writer)"

    def test_book_title_and_author_default_to_empty_strings(self) -> None:
        """Allow the default blank title and author values."""
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            category=self.category,
            price=Decimal("5.00"),
            description="A sample description.",
            stock=1,
        )

        assert book.title == ""
        assert book.author == ""

    def test_negative_book_price_is_currently_allowed(self) -> None:
        """Document that negative book prices are not rejected."""
        # Generated with AI, reviewed and modified
        book = Book.objects.create(
            category=self.category,
            title="Discounted",
            author="A. Writer",
            price=Decimal("-1.00"),
            description="A sample description.",
            stock=1,
        )

        book.refresh_from_db()
        assert book.price == Decimal("-1.00")


class TestOrderModel:
    """Test the Order model."""

    def setup_method(self) -> None:
        """Create an order and book for order tests."""
        self.order = Order.objects.create(
            first_name="Taylor",
            last_name="Reader",
            email="taylor@example.com",
        )
        self.category = Category.objects.create(
            name="Fiction",
            slug="fiction",
        )
        self.book = Book.objects.create(
            category=self.category,
            title="The Example",
            author="A. Writer",
            price=Decimal("10.00"),
            description="A sample description.",
            stock=5,
        )

    def test_create_order_with_optional_fields_omitted(self) -> None:
        """Use defaults for unpaid status and blank payment ID."""
        # Generated with AI, reviewed and modified
        assert self.order.pk is not None
        assert self.order.paid is False
        assert self.order.stripe_id == ""
        assert self.order.created_at is not None

    def test_order_string_representation(self) -> None:
        """Show the order ID in its string representation."""
        # Generated with AI, reviewed and modified
        assert str(self.order) == f"Order {self.order.pk}"

    def test_order_can_store_paid_status_and_payment_reference(self) -> None:
        """Save the paid status and payment reference."""
        # Generated with AI, reviewed and modified
        self.order.paid = True
        self.order.stripe_id = "payment-reference"
        self.order.save()
        self.order.refresh_from_db()

        assert self.order.paid is True
        assert self.order.stripe_id == "payment-reference"

    def test_order_without_items_has_zero_total(self) -> None:
        """Return zero when the order has no items."""
        # Generated with AI, reviewed and modified
        assert self.order.get_total_cost() == 0

    def test_order_total_sums_item_costs(self) -> None:
        """Sum the costs of all items in the order."""
        # Generated with AI, reviewed and modified
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("7.25"),
            quantity=2,
        )
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("3.50"),
            quantity=1,
        )

        assert self.order.get_total_cost() == Decimal("18.00")

    def test_deleting_order_cascades_to_its_items(self) -> None:
        """Delete an order's items when the order is deleted."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("10.00"),
            quantity=1,
        )
        item_id = item.pk

        self.order.delete()

        assert not OrderItem.objects.filter(pk=item_id).exists()


class TestOrderItemModel:
    """Test the OrderItem model."""

    def setup_method(self) -> None:
        """Create a book and order for item tests."""
        category = Category.objects.create(
            name="Fiction",
            slug="fiction",
        )
        self.book = Book.objects.create(
            category=category,
            title="The Example",
            author="A. Writer",
            price=Decimal("10.00"),
            description="A sample description.",
            stock=5,
        )
        self.order = Order.objects.create(
            first_name="Taylor",
            last_name="Reader",
            email="taylor@example.com",
        )

    def test_create_order_item_uses_default_quantity(self) -> None:
        """Create an item with the default quantity of one."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("10.00"),
        )

        assert item.pk is not None
        assert item.quantity == 1
        assert item.order == self.order
        assert item.book == self.book

    def test_order_item_string_representation(self) -> None:
        """Show the order item ID in its string representation."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("10.00"),
        )

        assert str(item) == str(item.pk)

    def test_order_item_cost_multiplies_price_by_quantity(self) -> None:
        """Multiply the item price by its quantity."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("12.50"),
            quantity=3,
        )

        assert item.get_cost() == Decimal("37.50")

    def test_zero_quantity_is_valid_and_costs_zero(self) -> None:
        """Allow zero quantity and calculate a zero cost."""
        # Generated with AI, reviewed and modified
        item = OrderItem(
            order=self.order,
            book=self.book,
            price=Decimal("12.50"),
            quantity=0,
        )
        item.full_clean()
        item.save()

        assert item.get_cost() == Decimal("0.00")

    def test_negative_quantity_fails_model_validation(self) -> None:
        """Reject a negative quantity during model validation."""
        # Generated with AI, reviewed and modified
        item = OrderItem(
            order=self.order,
            book=self.book,
            price=Decimal("12.50"),
            quantity=-1,
        )

        with pytest.raises(ValidationError):
            item.full_clean()

    def test_negative_order_item_price_is_currently_allowed(self) -> None:
        """Document that negative item prices are not rejected."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("-2.50"),
            quantity=2,
        )

        item.refresh_from_db()
        assert item.price == Decimal("-2.50")
        assert item.get_cost() == Decimal("-5.00")

    def test_deleting_book_cascades_to_its_order_items(self) -> None:
        """Delete a book's order items when the book is deleted."""
        # Generated with AI, reviewed and modified
        item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("10.00"),
            quantity=1,
        )
        item_id = item.pk

        self.book.delete()

        assert not OrderItem.objects.filter(pk=item_id).exists()
