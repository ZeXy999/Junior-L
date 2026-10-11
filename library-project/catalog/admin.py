from django.contrib import admin
from django.utils import timezone

from .models import Author, Book, BookCopy, Genre, Loan, Publisher, Review


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 0


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "birth_year", "death_year")
    search_fields = ("last_name", "first_name")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "publication_year", "pages", "created_at")
    list_filter = ("genre", "language", "publisher")
    search_fields = ("title", "isbn", "authors__last_name")
    filter_horizontal = ("authors",)
    inlines = [BookCopyInline]
    autocomplete_fields = ("publisher",)


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("book", "copy_number", "condition", "shelf")
    list_filter = ("condition",)
    search_fields = ("book__title",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("copy", "user", "borrowed_at", "due_date", "returned_at", "overdue")
    list_filter = ("returned_at",)
    search_fields = ("copy__book__title", "user__username")
    actions = ["mark_returned"]

    @admin.display(boolean=True, description="Overdue")
    def overdue(self, obj):
        return obj.is_overdue

    @admin.action(description="Mark selected loans as returned")
    def mark_returned(self, request, queryset):
        updated = queryset.filter(returned_at__isnull=True).update(returned_at=timezone.now())
        self.message_user(request, f"{updated} loan(s) marked as returned.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("book__title", "user__username", "comment")
