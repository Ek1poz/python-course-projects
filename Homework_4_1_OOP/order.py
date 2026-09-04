"""Class and methods for managing customer orders."""

from product import Product


class Order:
    """Represent a customer order."""

    def __init__(self) -> None:
        """Initialize an empty order."""
        self.list_of_products: list[tuple[Product, int]] = []
        self.order_amount: float = 0

    def add_product(self, new_product: Product, quantity: int = 1) -> None:
        """Add a product with the specified quantity to the order."""
        self.list_of_products.append((new_product, quantity))
        self.calculate_order_amount()

    def calculate_order_amount(self) -> float:
        """Calculate and return the total order amount."""
        self.order_amount = sum(
            product.price_of_product * quantity
            for product, quantity in self.list_of_products
        )

        return self.order_amount
