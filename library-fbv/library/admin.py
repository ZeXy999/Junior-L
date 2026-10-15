from django.contrib import admin
from django.utils.timezone import now

from .models import Author, Book, Publisher


class BookInline(admin.TabularInline):
    model = Book
    extra = 0
    fields = ('title', 'publication_date', 'genre', 'is_available')
    show_change_link = True
    fk_name = 'author'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'book_count', 'is_active')
    list_filter = ('birth_date',)
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('last_name', 'first_name')
    date_hierarchy = 'birth_date'
    inlines = [BookInline]

    @admin.display(description="Number of Books")
    def book_count(self, obj):
        return obj.books.count()

    @admin.display(boolean=True, description="Active")
    def is_active(self, obj):
        return obj.death_date is None


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'established', 'book_count')
    list_filter = ('country', 'established')
    search_fields = ('name', 'city', 'country')
    ordering = ('name',)

    @admin.display(description="Number of Books")
    def book_count(self, obj):
        return obj.books.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_date', 'is_available', 'rating', 'age')
    list_filter = ('genre', 'is_available', 'publication_date', 'author')
    search_fields = ('title', 'subtitle', 'isbn', 'author__first_name', 'author__last_name')
    ordering = ('-publication_date',)
    date_hierarchy = 'publication_date'
    list_editable = ('is_available', 'rating')
    list_per_page = 25
    save_on_top = True
    readonly_fields = ('created_at', 'updated_at', 'age')
    autocomplete_fields = ['author', 'publisher']
    actions = ['mark_as_available', 'mark_as_unavailable', 'increase_rating']

    @admin.display(description="Age")
    def age(self, obj):
        if not obj.publication_date:
            return "-"
        years = (now().date() - obj.publication_date).days // 365
        return f"{years} years" if years >= 0 else "Not yet published"

    @admin.action(description="Mark selected books as available")
    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} books marked as available.')

    @admin.action(description="Mark selected books as unavailable")
    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} books marked as unavailable.')

    @admin.action(description="Increase rating by 1")
    def increase_rating(self, request, queryset):
        for book in queryset:
            if book.rating < 5:
                book.rating += 1
                book.save()
        self.message_user(request, f'Rating increased for {queryset.count()} books.')
