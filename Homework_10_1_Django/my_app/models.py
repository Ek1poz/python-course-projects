from django.db import models


class Category(models.Model):
    """
    Model representing a book category.
    """
    name = models.CharField(max_length=100, verbose_name='name', default='')
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        """Returns the string representation of the category."""
        return str(self.name)


class Book(models.Model):
    """
    Model representing a specific book.
    Has a Many-to-One relationship with the Category model.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name='title', default='')
    author = models.CharField(max_length=100, verbose_name='author', default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='price', default='')
    description = models.TextField()
    stock = models.IntegerField()

    def __str__(self) -> str:
        """
        Returns the string representation
        of the book along with its author.
        """
        return f"{self.title} ({self.author})"
