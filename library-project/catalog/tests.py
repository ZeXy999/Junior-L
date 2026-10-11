from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Author, Book, BookCopy, Genre, Loan, Review


class CatalogTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Mystery", slug="mystery")
        self.author = Author.objects.create(first_name="Arthur", last_name="Doyle")
        self.book = Book.objects.create(title="The Hound", isbn="9780000000001", genre=self.genre,
                                        publication_year=1902, pages=256, summary="A spectral hound.")
        self.book.authors.add(self.author)
        self.copy1 = BookCopy.objects.create(book=self.book, copy_number=1)
        self.copy2 = BookCopy.objects.create(book=self.book, copy_number=2)
        self.user = User.objects.create_user("reader", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")

    def test_pages_render(self):
        for name, args in [("home", []), ("book-list", []), ("book-detail", [self.book.pk]),
                           ("author-list", []), ("author-detail", [self.author.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)

    def test_search_and_filters(self):
        url = reverse("book-list")
        self.assertContains(self.client.get(url, {"q": "doyle"}), "The Hound")
        self.assertNotContains(self.client.get(url, {"q": "zzzz"}), "The Hound")
        self.assertContains(self.client.get(url, {"genre": "mystery"}), "The Hound")

    def test_borrow_requires_login(self):
        response = self.client.post(reverse("book-borrow", args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])
        self.assertEqual(Loan.objects.count(), 0)

    def test_borrow_and_return(self):
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("book-borrow", args=[self.book.pk]))
        loan = Loan.objects.get()
        self.assertEqual(loan.user, self.user)
        self.assertEqual(Book.objects.with_stats().get(pk=self.book.pk).available_count, 1)
        self.client.post(reverse("loan-return", args=[loan.pk]))
        loan.refresh_from_db()
        self.assertIsNotNone(loan.returned_at)
        self.assertEqual(Book.objects.with_stats().get(pk=self.book.pk).available_count, 2)

    def test_cannot_borrow_same_book_twice(self):
        self.client.login(username="reader", password="pass12345")
        for _ in range(2):
            self.client.post(reverse("book-borrow", args=[self.book.pk]))
        self.assertEqual(Loan.objects.count(), 1)

    def test_no_copies_left(self):
        Loan.objects.create(copy=self.copy1, user=self.other)
        Loan.objects.create(copy=self.copy2, user=self.other)
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("book-borrow", args=[self.book.pk]))
        self.assertEqual(Loan.objects.filter(user=self.user).count(), 0)

    def test_overdue_flag(self):
        loan = Loan.objects.create(copy=self.copy1, user=self.user,
                                   due_date=timezone.localdate() - timedelta(days=3))
        self.assertTrue(loan.is_overdue)

    def test_review_create_update_and_average(self):
        self.client.login(username="reader", password="pass12345")
        url = reverse("book-review", args=[self.book.pk])
        self.client.post(url, {"rating": 5, "comment": "Wonderfully atmospheric."})
        self.client.post(url, {"rating": 3, "comment": "On reflection, merely good."})
        self.assertEqual(Review.objects.count(), 1)
        self.client.login(username="other", password="pass12345")
        self.client.post(url, {"rating": 5, "comment": "Still my favourite Holmes."})
        stats = Book.objects.with_stats().get(pk=self.book.pk)
        self.assertEqual(stats.review_count, 2)
        self.assertAlmostEqual(stats.avg_rating, 4.0)

    def test_short_review_rejected(self):
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("book-review", args=[self.book.pk]), {"rating": 4, "comment": "ok"})
        self.assertEqual(Review.objects.count(), 0)

    def test_signup_logs_in(self):
        response = self.client.post(reverse("signup"), {
            "username": "newbie", "email": "n@example.com",
            "password1": "S0me-strong-pass!", "password2": "S0me-strong-pass!"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertEqual(self.client.get(reverse("my-library")).status_code, 200)
