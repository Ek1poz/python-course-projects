from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Model representing a custom user.
    """
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        verbose_name=_('phone number')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('date of birth')
    )

    def __str__(self) -> str:
        """
        Returns the string representation of the user.
        """
        return self.username


class Category(models.Model):
    """
    Model representing a book category.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('name'),
        default=''
    )
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the category.
        """
        return str(self.name)


class Book(models.Model):
    """
    Model representing a specific book.
    Has a Many-to-One relationship with the Category model.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=100,
        verbose_name=_('title'),
        default=''
    )
    author = models.CharField(
        max_length=100,
        verbose_name=_('author'),
        default=''
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('price'),
        default=''
    )
    description = models.TextField()
    stock = models.IntegerField()

    def __str__(self) -> str:
        """
        Returns the string representation
        of the book along with its author.
        """
        return f"{self.title} ({self.author})"


class Order(models.Model):
    """
    Model representing a customer's order.
    """
    first_name = models.CharField(
        max_length=50,
        verbose_name=_('First name')
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name=_('Last name')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    paid = models.BooleanField(
        default=False,
        verbose_name=_('Paid')
    )
    stripe_id = models.CharField(
        max_length=250, blank=True, verbose_name=_("ID of payment Stripe")
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """
        Return the string representation of the order.
        """
        return f"Order {self.id}"

    def get_total_cost(self):
        """
        Calculate the total cost of all items in the order.
        """
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """
    Model representing a single item within an order.
    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(
        Book,
        related_name='order_items',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Price")
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity")
    )

    def __str__(self):
        """
        Return the string representation of the order item.
        """
        return str(self.id)

    def get_cost(self):
        """
        Calculate the total cost for this specific item.
        """
        return self.price * self.quantity