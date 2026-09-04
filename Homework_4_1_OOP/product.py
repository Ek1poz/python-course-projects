"""Class for representing products in the store."""


class Product:
    """Represent a product in the store."""

    def __init__(
        self,
        name_of_product: str,
        category_of_product: str,
        price_of_product: float,
        quantity_in_stock: int,
    ) -> None:
        """Initialize a product."""
        self.name_of_product = name_of_product
        self.category_of_product = category_of_product
        self.price_of_product = price_of_product
        self.quantity_in_stock = quantity_in_stock

    def set_price_of_product(self, new_price: float) -> None:
        """Change the product price."""
        self.price_of_product = new_price

    def set_quantity_in_stock(self, new_quantity: int) -> None:
        """Change the product stock quantity."""
        self.quantity_in_stock = new_quantity
