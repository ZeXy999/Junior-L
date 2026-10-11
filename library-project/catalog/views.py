from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import ReviewForm, SignUpForm
from .models import (LOAN_DAYS, MAX_ACTIVE_LOANS, Author, Book, BookCopy, Genre, Loan,
                     Review)


class HomeView(TemplateView):
    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.with_stats().select_related("genre").prefetch_related("authors")
        context["top_rated"] = books.filter(review_count__gte=2).order_by(
            F("avg_rating").desc(nulls_last=True), "-review_count")[:6]
        context["newest"] = books.order_by("-created_at", "title")[:6]
        context["most_reviewed"] = books.order_by("-review_count", "title")[:6]
        context["genres"] = Genre.objects.annotate(n=Count("books")).filter(n__gt=0)
        context["stats"] = {
            "books": Book.objects.count(),
            "authors": Author.objects.count(),
            "copies": BookCopy.objects.count(),
            "reviews": Review.objects.count(),
            "on_loan": Loan.objects.filter(returned_at__isnull=True).count(),
        }
        return context


class BookListView(ListView):
    template_name = "catalog/book_list.html"
    context_object_name = "books"
    paginate_by = 12

    SORTS = {
        "title": ["title"],
        "newest": ["-publication_year", "title"],
        "oldest": ["publication_year", "title"],
        "rating": [F("avg_rating").desc(nulls_last=True), "-review_count", "title"],
        "popular": ["-review_count", "title"],
        "added": ["-created_at", "title"],
    }

    def get_queryset(self):
        qs = Book.objects.with_stats().select_related("genre").prefetch_related("authors")
        params = self.request.GET
        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(subtitle__icontains=q) | Q(isbn__icontains=q)
                | Q(authors__first_name__icontains=q) | Q(authors__last_name__icontains=q)
            ).distinct()
        genre = params.get("genre")
        if genre:
            qs = qs.filter(genre__slug=genre)
        if params.get("available") == "1":
            qs = qs.filter(available_count__gt=0)
        return qs.order_by(*self.SORTS.get(params.get("sort"), self.SORTS["title"]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["genres"] = Genre.objects.all()
        context["q"] = self.request.GET.get("q", "")
        context["current_genre"] = self.request.GET.get("genre", "")
        context["current_sort"] = self.request.GET.get("sort", "title")
        context["only_available"] = self.request.GET.get("available") == "1"
        context["result_count"] = context["paginator"].count
        return context


class BookDetailView(DetailView):
    template_name = "catalog/book_detail.html"
    context_object_name = "book"
    queryset = (Book.objects.with_stats().select_related("publisher", "genre")
                .prefetch_related("authors"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        user = self.request.user
        context["reviews"] = book.reviews.select_related("user")
        context["copies"] = book.copies.prefetch_related("loans")
        context["rating_breakdown"] = self.rating_breakdown(book)
        context["related"] = (Book.objects.with_stats().filter(genre=book.genre)
                              .exclude(pk=book.pk).prefetch_related("authors")[:6]
                              if book.genre_id else [])
        context["user_loan"] = None
        context["review_form"] = ReviewForm()
        if user.is_authenticated:
            context["user_loan"] = Loan.objects.filter(
                user=user, copy__book=book, returned_at__isnull=True).first()
            existing = book.reviews.filter(user=user).first()
            context["user_review"] = existing
            if existing:
                context["review_form"] = ReviewForm(instance=existing)
        context["loan_days"] = LOAN_DAYS
        return context

    @staticmethod
    def rating_breakdown(book):
        counts = dict(book.reviews.values_list("rating").annotate(n=Count("pk")))
        total = sum(counts.values()) or 1
        return [{"stars": s, "count": counts.get(s, 0), "pct": round(100 * counts.get(s, 0) / total)}
                for s in range(5, 0, -1)]


class AuthorListView(ListView):
    template_name = "catalog/author_list.html"
    context_object_name = "authors"
    paginate_by = 24
    queryset = Author.objects.annotate(book_total=Count("books")).filter(book_total__gt=0)


class AuthorDetailView(DetailView):
    template_name = "catalog/author_detail.html"
    model = Author
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["books"] = (Book.objects.with_stats().filter(authors=self.object)
                            .select_related("genre").prefetch_related("authors"))
        return context


class MyLibraryView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/my_library.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loans = Loan.objects.filter(user=self.request.user).select_related("copy__book")
        context["active_loans"] = loans.filter(returned_at__isnull=True).order_by("due_date")
        context["history"] = loans.filter(returned_at__isnull=False)[:20]
        context["my_reviews"] = (Review.objects.filter(user=self.request.user)
                                 .select_related("book"))
        context["max_loans"] = MAX_ACTIVE_LOANS
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Welcome, {self.object.username}! Your account is ready.")
        return response


@login_required
@require_POST
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    with transaction.atomic():
        active = Loan.objects.filter(user=request.user, returned_at__isnull=True)
        if active.filter(copy__book=book).exists():
            messages.info(request, "You already have this book.")
        elif active.count() >= MAX_ACTIVE_LOANS:
            messages.error(request, f"You can borrow at most {MAX_ACTIVE_LOANS} books at a time.")
        else:
            copy = book.copies.available().first()
            if copy is None:
                messages.error(request, "Sorry, every copy of this book is currently on loan.")
            else:
                loan = Loan.objects.create(copy=copy, user=request.user)
                messages.success(
                    request, f"You borrowed \u201c{book.title}\u201d. Please return it by "
                             f"{loan.due_date:%d %b %Y}.")
    return redirect(book)


@login_required
@require_POST
def return_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk, user=request.user, returned_at__isnull=True)
    loan.returned_at = timezone.now()
    loan.save(update_fields=["returned_at"])
    messages.success(request, f"Thanks for returning \u201c{loan.copy.book.title}\u201d.")
    return redirect(request.POST.get("next") or "my-library")


@login_required
@require_POST
def review_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    existing = Review.objects.filter(book=book, user=request.user).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.book = book
        review.user = request.user
        review.save()
        messages.success(request, "Thanks \u2013 your review has been saved.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    return redirect(book)
