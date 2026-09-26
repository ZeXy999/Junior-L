from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import Author, Publisher, Genre, Book, BookAuthor, BookCopy, Review


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 0
    fields = ('copy_number', 'condition', 'is_borrowed', 'borrowed_by', 'due_date')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'book_count', 'is_active')
    list_filter = ('birth_date',)
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('last_name', 'first_name')
    date_hierarchy = 'birth_date'

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Number of Books"

    def is_active(self, obj):
        return obj.death_date is None
    is_active.boolean = True
    is_active.short_description = "Active"


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'established', 'book_count')
    list_filter = ('country', 'established')
    search_fields = ('name', 'city', 'country')
    ordering = ('name',)

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Number of Books"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'display_authors', 'genre', 'publication_date',
        'is_available', 'rating', 'age'
    )
    list_filter = ('genre', 'is_available', 'publication_date')
    search_fields = ('title', 'subtitle', 'isbn')
    ordering = ('-publication_date',)
    date_hierarchy = 'publication_date'
    list_editable = ('is_available', 'rating')
    list_per_page = 25
    save_on_top = True
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BookAuthorInline, BookCopyInline]
    actions = ['mark_as_available', 'mark_as_unavailable', 'increase_rating']

    def display_authors(self, obj):
        return ", ".join(str(a) for a in obj.authors.all())
    display_authors.short_description = "Authors"

    def age(self, obj):
        years = (now().date() - obj.publication_date).days // 365
        return f"{years} years" if years >= 0 else "Not yet published"
    age.short_description = "Age"

    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} books marked as available.')
    mark_as_available.short_description = "Mark selected books as available"

    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} books marked as unavailable.')
    mark_as_unavailable.short_description = "Mark selected books as unavailable"

    def increase_rating(self, request, queryset):
        for book in queryset:
            if book.rating < 5:
                book.rating += 1
                book.save()
        self.message_user(request, f'Rating increased for {queryset.count()} books.')
    increase_rating.short_description = "Increase rating by 1"


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('book', 'copy_number', 'condition', 'is_borrowed', 'borrowed_by', 'due_date')
    list_filter = ('condition', 'is_borrowed')
    search_fields = ('book__title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('book__title', 'user__username', 'comment')
