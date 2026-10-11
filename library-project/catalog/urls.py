from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("books/", views.BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/borrow/", views.borrow_book, name="book-borrow"),
    path("books/<int:pk>/review/", views.review_book, name="book-review"),
    path("loans/<int:pk>/return/", views.return_loan, name="loan-return"),
    path("authors/", views.AuthorListView.as_view(), name="author-list"),
    path("authors/<int:pk>/", views.AuthorDetailView.as_view(), name="author-detail"),
    path("my-library/", views.MyLibraryView.as_view(), name="my-library"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]
