"""Class for representing store customers."""

from order import Order


class Customer:
    """Represent a store customer."""

    def __init__(self, name_of_customer: str, email_of_customer: str) -> None:
        """Initialize a customer."""
        self.name_of_customer = name_of_customer
        self.email_of_customer = email_of_customer
        self.list_of_orders: list[Order] = []

    def add_order(self, new_order: Order) -> None:
        """Add an order to the customer's order list."""
        self.list_of_orders.append(new_order)
