from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    established = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    GENRE_CHOICES = [
        ('F', 'Fiction'), ('NF', 'Non-Fiction'), ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'), ('MYS', 'Mystery'), ('THR', 'Thriller'),
        ('ROM', 'Romance'), ('HIS', 'Historical'), ('BIO', 'Biography'),
        ('SCI', 'Science'), ('TEC', 'Technology'),
    ]

    title = models.CharField(max_length=200, help_text="The book's full title")
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True,
                            help_text="The book's unique 13-digit ISBN")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='books')
    publication_date = models.DateField()
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default='F')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    summary = models.TextField(help_text="Brief description of the book")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    is_available = models.BooleanField(default=True)
    borrowed_count = models.IntegerField(default=0)
    rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5",
    )
    # Step 10: optional per-user ownership, enforced by the edit/delete views.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='books_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('library:book-detail', kwargs={'pk': self.pk})

    def full_title(self):
        if self.subtitle:
            return f"{self.title}: {self.subtitle}"
        return self.title

    def is_recent(self):
        return (timezone.now().date() - self.publication_date).days < 1825

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['genre']),
        ]
