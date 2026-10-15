from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookModelForm, BookSearchForm
from .models import Author, Book


# ---------------------------------------------------------------- 5a: display views

def book_list(request):
    """
    Display a searchable, filterable, paginated list of books.
    """
    search_form = BookSearchForm(request.GET or None)
    books = Book.objects.select_related('author', 'publisher').all()

    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    sort_by = request.GET.get('sort', 'title')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(isbn__icontains=query)
        )

    if genre:
        books = books.filter(genre=genre)

    sort_mapping = {
        'title': 'title',
        '-title': '-title',
        '-rating': '-rating',
        '-publication_date': '-publication_date',
        'publication_date': 'publication_date',
    }
    # A secondary key keeps the order stable (and pagination consistent) when values tie.
    books = books.order_by(sort_mapping.get(sort_by, 'title'), 'pk')

    paginator = Paginator(books, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'search_query': query,
        'genre': genre,
        'sort_by': sort_by,
        # Preserve filters across pagination links without the 'page' key.
        'query_params': _params_without_page(request),
    }
    return render(request, 'library/book_list.html', context)


def book_detail(request, pk):
    """
    Display detailed information about a single book, plus similar titles.
    """
    book = get_object_or_404(
        Book.objects.select_related('author', 'publisher'),
        pk=pk
    )

    similar_books = Book.objects.filter(
        genre=book.genre
    ).exclude(pk=book.pk).order_by('-rating')[:4]

    context = {
        'book': book,
        'similar_books': similar_books,
    }
    return render(request, 'library/book_detail.html', context)


# ---------------------------------------------------------------- 5b: edit views

@login_required
def book_create(request):
    """
    Create a new book. GET displays the empty form, POST processes it.
    """
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            book = form.save(commit=False)
            if hasattr(book, 'created_by'):
                book.created_by = request.user
            book.save()
            form.save_m2m()
            messages.success(request, f'"{book.title}" was added to the library.')
            return redirect('library:book-detail', pk=book.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = BookModelForm(user=request.user)

    return render(request, 'library/book_form.html', {
        'form': form,
        'title': 'Add a Book',
        'submit_text': 'Create Book',
    })


@login_required
def book_update(request, pk):
    """
    Update an existing book. Only the creator or staff may edit it.
    """
    book = get_object_or_404(Book, pk=pk)

    if hasattr(book, 'created_by'):
        if not request.user.is_staff and book.created_by != request.user:
            raise PermissionDenied("You don't have permission to edit this book.")

    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, instance=book, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" was updated.')
            return redirect('library:book-detail', pk=book.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = BookModelForm(instance=book, user=request.user)

    return render(request, 'library/book_form.html', {
        'form': form,
        'book': book,
        'title': f'Edit "{book.title}"',
        'submit_text': 'Save Changes',
    })


@login_required
def book_delete(request, pk):
    """
    Confirm and delete a book. GET shows a confirmation page,
    POST performs the deletion.
    """
    book = get_object_or_404(Book, pk=pk)

    if hasattr(book, 'created_by'):
        if not request.user.is_staff and book.created_by != request.user:
            raise PermissionDenied("You don't have permission to delete this book.")

    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" was removed from the library.')
        return redirect('library:book-list')

    return render(request, 'library/book_confirm_delete.html', {'book': book})


# ---------------------------------------------------------------- 5c: optional extras

def book_search_ajax(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__last_name__icontains=query)
    ).select_related('author')[:10]

    results = [
        {'id': b.id, 'title': b.title, 'author': str(b.author)}
        for b in books
    ]
    return JsonResponse({'results': results})


@require_POST
@login_required
def book_toggle_availability(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.is_available = not book.is_available
    book.save(update_fields=['is_available'])
    return JsonResponse({'success': True, 'is_available': book.is_available})


def _params_without_page(request):
    """Return the current GET querystring with 'page' stripped out."""
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()
