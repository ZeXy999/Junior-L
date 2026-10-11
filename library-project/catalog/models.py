from datetime import timedelta

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

LOAN_DAYS = 14
MAX_ACTIVE_LOANS = 5


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def lifespan(self):
        if self.birth_year and self.death_year:
            return f"{self.birth_year}\u2013{self.death_year}"
        if self.birth_year:
            return f"born {self.birth_year}"
        return ""

    def get_absolute_url(self):
        return reverse("author-detail", args=[self.pk])


class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BookQuerySet(models.QuerySet):
    def with_stats(self):
        """Annotate rating, review count and copy availability using subqueries."""
        reviews = Review.objects.filter(book=OuterRef("pk")).order_by().values("book")
        copies = BookCopy.objects.filter(book=OuterRef("pk")).order_by().values("book")
        free = copies.exclude(pk__in=Loan.objects.filter(returned_at__isnull=True).values("copy_id"))
        return self.annotate(
            avg_rating=Subquery(reviews.annotate(a=Avg("rating")).values("a"),
                                output_field=models.FloatField()),
            review_count=Coalesce(Subquery(reviews.annotate(c=Count("pk")).values("c"),
                                           output_field=IntegerField()), Value(0)),
            copy_count=Coalesce(Subquery(copies.annotate(c=Count("pk")).values("c"),
                                         output_field=IntegerField()), Value(0)),
            available_count=Coalesce(Subquery(free.annotate(c=Count("pk")).values("c"),
                                              output_field=IntegerField()), Value(0)),
        )


class Book(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="books")
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="books")
    publication_year = models.IntegerField()
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default="English")
    summary = models.TextField()
    cover = models.ImageField(upload_to="covers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ["title"]
        indexes = [models.Index(fields=["title"]), models.Index(fields=["publication_year"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book-detail", args=[self.pk])

    @property
    def author_names(self):
        return ", ".join(a.full_name for a in self.authors.all())


class BookCopyQuerySet(models.QuerySet):
    def available(self):
        """Copies that are not currently out on loan."""
        return self.exclude(pk__in=Loan.objects.filter(returned_at__isnull=True).values("copy_id"))


class BookCopy(models.Model):
    CONDITION_CHOICES = [("E", "Excellent"), ("G", "Good"), ("F", "Fair"), ("P", "Poor")]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    copy_number = models.PositiveIntegerField()
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, default="G")
    shelf = models.CharField(max_length=40, blank=True)

    objects = BookCopyQuerySet.as_manager()

    class Meta:
        ordering = ["book", "copy_number"]
        unique_together = [["book", "copy_number"]]
        verbose_name_plural = "book copies"

    def __str__(self):
        return f"{self.book.title} \u2013 copy #{self.copy_number}"

    @property
    def active_loan(self):
        return self.loans.filter(returned_at__isnull=True).first()

    @property
    def is_available(self):
        return not self.loans.filter(returned_at__isnull=True).exists()


def default_due_date():
    return timezone.localdate() + timedelta(days=LOAN_DAYS)


class Loan(models.Model):
    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name="loans")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loans")
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(default=default_due_date)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]

    def __str__(self):
        return f"{self.user} borrowed {self.copy}"

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def is_overdue(self):
        return self.is_active and self.due_date < timezone.localdate()

    @property
    def days_left(self):
        return (self.due_date - timezone.localdate()).days


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["book", "user"]]

    def __str__(self):
        return f"{self.user} \u2013 {self.book} ({self.rating}/5)"
