"""Main module for running the store application."""

from excel_manager import read_data_from_excel
from order import Order


def main() -> None:
    """Run the store application."""
    products, customers = read_data_from_excel("data.xlsx")

    print("---------- PRODUCTS ----------")

    for product in products:
        print(
            f"Name: {product.name_of_product}\n"
            f"Category: {product.category_of_product}\n"
            f"Price: {product.price_of_product}\n"
            f"Quantity in stock: {product.quantity_in_stock}\n"
            "-----------------------------"
        )

    print("\n---------- CUSTOMERS ----------")

    for customer in customers:
        print(
            f"Name: {customer.name_of_customer}\n"
            f"Email: {customer.email_of_customer}\n"
            f"Orders: {len(customer.list_of_orders)}\n"
        )

    # Add new Order
    order = Order()

    if len(products) >= 3:
        order.add_product(products[0], 2)
        order.add_product(products[1], 3)
        order.add_product(products[2], 1)

    print("\n\n---------- ORDER ----------")

    for product, quantity in order.list_of_products:
        total_price = product.price_of_product * quantity

        print(f"{product.name_of_product} x {quantity} = {total_price}")

    print("-----------------------------")
    print(f"Total order amount: {order.order_amount}")

    # Further customization (Add order to a
    # customer or change info about product)
    if customers:
        customers[0].add_order(order)

        print("\n---------- CUSTOMER ORDER ----------")
        print(f"Customer: {customers[0].name_of_customer}")
        print(f"Email: {customers[0].email_of_customer}")
        print(f"Number of orders: {len(customers[0].list_of_orders)}")

    if products:
        products[0].set_price_of_product(23000)
        products[0].set_quantity_in_stock(15)

        print("\n---------- UPDATED PRODUCT ----------")
        print(f"Name: {products[0].name_of_product}")
        print(f"New price: {products[0].price_of_product}")
        print(f"New quantity: {products[0].quantity_in_stock}")


if __name__ == "__main__":
    main()
