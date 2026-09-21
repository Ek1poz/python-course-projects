from django.contrib import admin
from my_app.models import Category, Book


class BookInLine(admin.TabularInline):
    """
        Inline display for quickly adding books directly
        on the category editing page.
    """
    model = Book
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
        Admin panel configuration for the Category model.
        Includes slug auto-population and book inline setup.
    """
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    inlines = [BookInLine]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
        Admin panel configuration for the Book model.
        Provides filtering, search, and list display configurations.
    """
    list_display = ('title', 'author', 'price', 'stock', 'category')
    list_filter = ('category', 'author')

    search_fields = ('title', 'author')