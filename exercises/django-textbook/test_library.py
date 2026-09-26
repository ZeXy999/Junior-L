import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_first_project.settings")
django.setup()

from datetime import date
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth.models import User
from library.models import Author, Publisher, Genre, Book, BookAuthor, BookCopy, Review

print("=== 2.6 CREATE ===")
orwell, created = Author.objects.get_or_create(
    first_name="George", last_name="Orwell",
    defaults={
        'birth_date': date(1903, 6, 25),
        'death_date': date(1950, 1, 21),
        'biography': "British novelist and essayist, journalist and critic.",
    }
)
print(f"Author: {orwell} (created={created})")

lee, _ = Author.objects.get_or_create(
    first_name="Harper", last_name="Lee",
    defaults={'birth_date': date(1926, 4, 28), 'biography': "American novelist."}
)

secker, _ = Publisher.objects.get_or_create(
    name="Secker & Warburg", defaults={'city': "London", 'country': "UK", 'established': date(1936, 1, 1)}
)
lippincott, _ = Publisher.objects.get_or_create(
    name="J. B. Lippincott & Co.", defaults={'city': "Philadelphia", 'country': "USA"}
)

fiction, _ = Genre.objects.get_or_create(name="Fiction")
scifi, _ = Genre.objects.get_or_create(name="Science Fiction", parent=fiction)

book1, created1 = Book.objects.get_or_create(
    isbn="9780451524935",
    defaults={
        'title': "Nineteen Eighty-Four", 'publisher': secker, 'genre': scifi,
        'publication_date': date(1949, 6, 8), 'pages': 328,
        'summary': "A dystopian social science fiction novel.", 'rating': 5,
    }
)
if created1:
    BookAuthor.objects.create(book=book1, author=orwell, contribution_type='A', contribution_order=1)
print(f"Book: {book1} (created={created1})")

book2, created2 = Book.objects.get_or_create(
    isbn="9780061120084",
    defaults={
        'title': "To Kill a Mockingbird", 'subtitle': "A Novel", 'publisher': lippincott, 'genre': fiction,
        'publication_date': date(1960, 7, 11), 'pages': 336,
        'summary': "The story of young Scout Finch and her father, Atticus.", 'rating': 5,
    }
)
if created2:
    BookAuthor.objects.create(book=book2, author=lee, contribution_type='A', contribution_order=1)
print(f"Book: {book2} (created={created2}), full_title(): {book2.full_title()}")

print("\n=== 2.6 READ / field lookups ===")
print("All books:", list(Book.objects.all()))
print("Fiction genre books:", list(Book.objects.filter(genre__name='Fiction')))
print("Books with 'Mockingbird' in title:", list(Book.objects.filter(title__icontains='mockingbird')))
print("High rated (>=5):", list(Book.objects.filter(rating__gte=5)))
print("Q OR query (rating=5 OR genre=Science Fiction):",
      list(Book.objects.filter(Q(rating=5) | Q(genre__name='Science Fiction')).distinct()))

print("\n=== 2.7 Relationships ===")
print("Orwell's books (reverse FK via through):", list(orwell.books.all()))
print("Book1 authors (M2M forward):", list(book1.authors.all()))
print("Book1 -> publisher:", book1.publisher)
print("Genre subgenres of Fiction:", list(fiction.subgenres.all()))

print("\n=== BookCopy + borrowing ===")
user, _ = User.objects.get_or_create(username="juniortest")
copy1, _ = BookCopy.objects.get_or_create(book=book1, copy_number=1, defaults={'condition': 'G'})
print(f"Copy: {copy1}, can_be_borrowed: {book1.can_be_borrowed()}")

print("\n=== Review + average_rating() ===")
Review.objects.get_or_create(book=book1, user=user, defaults={'rating': 4, 'comment': "Chilling and prescient."})
print(f"book1.average_rating(): {book1.average_rating()}")

print("\n=== Aggregation ===")
stats = Book.objects.aggregate(total_books=Count('id'), avg_pages=Avg('pages'), total_pages=Sum('pages'))
print("Aggregate stats:", stats)
genre_counts = Book.objects.values('genre__name').annotate(count=Count('id'))
print("Books per genre:", list(genre_counts))

print("\n=== select_related / prefetch_related sanity check ===")
books_qs = Book.objects.select_related('publisher', 'genre').prefetch_related('authors')
for b in books_qs:
    print(f"- {b.title} | publisher={b.publisher} | genre={b.genre} | authors={list(b.authors.all())} | age={b.age}yrs")

print("\nALL TESTS PASSED")
