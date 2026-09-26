from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


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


class Genre(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='subgenres'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class BookAuthor(models.Model):
    CONTRIBUTION_CHOICES = [
        ('A', 'Author'), ('E', 'Editor'), ('C', 'Contributor'),
        ('F', 'Foreword'), ('I', 'Introduction'), ('T', 'Translator'),
    ]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    contribution_type = models.CharField(
        max_length=1, choices=CONTRIBUTION_CHOICES, default='A'
    )
    contribution_order = models.IntegerField(default=1)
    royalty_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    class Meta:
        ordering = ['contribution_order']
        unique_together = [['book', 'author', 'contribution_type']]

    def __str__(self):
        return f"{self.author} - {self.get_contribution_type_display()} of {self.book}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, through=BookAuthor, related_name='books')
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='books'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='books'
    )
    publication_date = models.DateField()
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='English')
    summary = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    borrowed_count = models.IntegerField(default=0)
    rating = models.IntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def full_title(self):
        return f"{self.title}: {self.subtitle}" if self.subtitle else self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return None

    def can_be_borrowed(self):
        return self.is_available and self.copies.filter(is_borrowed=False).exists()

    @property
    def age(self):
        from django.utils import timezone
        return (timezone.now().date() - self.publication_date).days // 365

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['is_available']),
        ]


class BookCopy(models.Model):
    CONDITION_CHOICES = [
        ('E', 'Excellent'), ('G', 'Good'), ('F', 'Fair'),
        ('P', 'Poor'), ('D', 'Damaged'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    copy_number = models.PositiveIntegerField()
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, default='G')
    location = models.CharField(max_length=100, blank=True)
    is_borrowed = models.BooleanField(default=False)
    borrowed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='borrowed_copies'
    )
    borrowed_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Copy #{self.copy_number} of {self.book.title}"

    class Meta:
        ordering = ['book', 'copy_number']
        unique_together = [['book', 'copy_number']]


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review of {self.book.title} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        unique_together = [['book', 'user']]
