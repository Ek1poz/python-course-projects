from decimal import Decimal
from typing import Iterator, Dict, Any
from django.conf import settings
from django.http import HttpRequest
from .models import Book


class Cart:
    """
    Session-based shopping cart for managing items before checkout.
    """
    def __init__(self, request: HttpRequest) -> None:
        """
        Initialize the cart using the request session.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: Dict[str, Dict[str, Any]] = cart

    def add(
        self, book: Book, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        """
        Add a product to the cart or update its quantity.
        """
        book_id: str = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {"quantity": 0, "price": str(book.price)}

        if override_quantity:
            self.cart[book_id]["quantity"] = quantity
        else:
            self.cart[book_id]["quantity"] += quantity
        self.save()

    def save(self) -> None:
        """
        Mark the session as modified to ensure it gets saved.
        """
        self.session.modified = True

    def remove(self, book: Book) -> None:
        """
        Remove a product from the cart.
        """
        book_id: str = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def clear(self) -> None:
        """
        Clear all items from the cart session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterate over the items in the cart and fetch products from the database.
        """
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids)
        cart = self.cart.copy()

        for book in books:
            cart[str(book.id)]["book"] = book

        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def get_total_price(self) -> int:
        """
        Calculate the total price of all items currently in the cart.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )