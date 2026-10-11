# Chapter 3: Views and Templates

*Function-based and class-based views, Django's generic views, the templating language, and the form system that connects users to your application.*

## Chapter Contents

- 3.1 Introduction to Views
- 3.2 Function-Based Views
- 3.3 Class-Based Views
- 3.4 Generic Display Views
- 3.5 Generic Edit Views
- 3.6 Template Fundamentals
- 3.7 Advanced Template Features
- 3.8 Forms in Django
- 3.9 Chapter Summary and What's Next

## 3.1 Introduction to Views

In this section, we establish the conceptual foundation for everything that follows: what views are, why they matter, and how they fit into Django's architecture.

### The Role of Views

In Django's MTV architecture, the view is responsible for the business logic of your application — the bridge between your data (models) and your presentation (templates).

**What Views Do:**

- Receive HTTP Requests: the view is the entry point for every request.
- Process Data: retrieve data from the database, perform calculations, manipulate data.
- Handle User Input: process form submissions, query parameters, and URL parameters.
- Make Decisions: decide what to display based on authentication, permissions, and business rules.
- Render Responses: return HTML pages, JSON data, redirects, file downloads, etc.

**What Views Should Not Do:**

- Database schema logic — that belongs to models.
- Presentation logic — that belongs to templates.
- Business logic complexity — keep views lean; complex logic belongs in models or services.

### The Request-Response Cycle in Detail

```
1. Browser sends HTTP request -> Django server
2. Middleware processes request (session, authentication, CSRF, etc.)
3. URL dispatcher matches the path to a view
4. View is called with the request and any captured parameters
5. View executes its logic:
   a. Query database (using models)
   b. Process data
   c. Validate user input
   d. Check permissions
6. View prepares a context dictionary
7. View renders a template with the context
8. Response is returned (HTML, JSON, redirect, etc.)
9. Middleware processes response
10. Browser receives and displays the response
```

### Function-Based Views vs. Class-Based Views

**Function-Based Views (FBVs):**

```python
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Book

def book_list(request):
    """Display a list of all books."""
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

def book_detail(request, pk):
    """Display details of a single book."""
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})
```

Characteristics: simple and straightforward, easy for beginners, explicit and transparent, but can become repetitive for similar views.

**Class-Based Views (CBVs):**

```python
from django.views.generic import ListView, DetailView
from .models import Book

class BookListView(ListView):
    """Display a list of all books."""
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'

class BookDetailView(DetailView):
    """Display details of a single book."""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
```

Characteristics: more powerful and flexible, encourage code reuse through inheritance and mixins, more concise for common patterns, but a steeper learning curve.

| Use FBVs When | Use CBVs When |
|---|---|
| You're new to Django | You have experience with OOP |
| Views are simple and unique | Views follow common patterns |
| You need maximum clarity | You need maximum reusability |
| You have minimal logic | You have complex, reusable logic |

Recommendation: start with function-based views to understand the fundamentals, then gradually adopt class-based views for their power and efficiency. Many experienced developers use a mix of both.

### The Request Object

The request object is the first parameter of every view function and contains all information about the incoming HTTP request.

```python
def my_view(request):
    method = request.method # GET, POST, PUT, DELETE, etc.

    query_params = request.GET # Query string
    search_term = request.GET.get('q', '')

    post_data = request.POST # Form submission
    username = request.POST.get('username')

    user = request.user # Authenticated or anonymous
    is_authenticated = user.is_authenticated

    session_data = request.session
    request.session['visited'] = True

    cookie_value = request.COOKIES.get('my_cookie')
    user_agent = request.META.get('HTTP_USER_AGENT')

    path = request.path
    full_path = request.get_full_path()
    host = request.get_host()

    uploaded_file = request.FILES.get('file')
```

### The Response Object

Views return an HttpResponse object (or a subclass), which contains the content, status code, and headers of the response.

```python
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

def simple_view(request):
    return HttpResponse("<h1>Hello, World!</h1>")

def template_view(request):
    return render(request, 'template.html', {'context': 'data'})

def json_view(request):
    data = {'name': 'John', 'age': 30}
    return JsonResponse(data)

def redirect_view(request):
    return redirect('book-list') # Named URL
# return redirect('/books/') # A path
# return redirect('https://example.com') # External redirect

def file_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="book.pdf"'
    return response
```

### The Shortcut Functions

```python
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/list.html', {'books': books})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/detail.html', {'book': book})

def author_books(request, author_id):
    books = get_list_or_404(Book, author_id=author_id)
    return render(request, 'books/list.html', {'books': books})

def save_and_redirect(request):
    return redirect('book-list')
```

### URL Parameters and Capture

```python
# urls.py
path('books/<int:pk>/', views.book_detail, name='book-detail')
path('books/<slug:slug>/', views.book_detail_slug, name='book-detail-slug')
path('author/<str:name>/', views.author_books, name='author-books')
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/detail.html', {'book': book})

def author_books(request, name):
    books = Book.objects.filter(author__first_name=name)
    return render(request, 'books/list.html', {'books': books})
```

| Converter | Description | Example |
|---|---|---|
| str | Any string (slashes excluded) | path('<str:name>/', ...) |
| int | Integer | path('<int:pk>/', ...) |
| slug | Letters, numbers, hyphens, underscores | path('<slug:slug>/', ...) |
| uuid | UUID | path('<uuid:uuid>/', ...) |
| path | Any string (slashes included) | path('<path:path>/', ...) |

### The url Template Tag

```html
{% url 'book-detail' pk=book.id %}
{% url 'book-detail' book.id %}
{% url 'author-books' name='John' %}
```

```python
from django.urls import reverse
url = reverse('book-detail', kwargs={'pk': 1})
url = reverse('book-detail', args=[1])
```

### URL Namespacing

```python
# urls.py (app level)
app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('<int:pk>/', views.book_detail, name='detail'),
]

# urls.py (project level)
urlpatterns = [
    path('books/', include('books.urls', namespace='books')),
    path('magazines/', include('magazines.urls', namespace='magazines')),
]
```

```html
{% url 'books:list' %}
{% url 'books:detail' pk=1 %}
```

### View Decorators

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_GET

@login_required
def profile_view(request):
    return render(request, 'profile.html')

@permission_required('books.can_publish')
def publish_book(request, pk):
    return render(request, 'publish.html')

@require_http_methods(['GET', 'POST'])
def submit_view(request):
    pass

@require_POST
def delete_book(request, pk):
    pass

@cache_page(60 * 15) # Cache for 15 minutes
def slow_view(request):
    return render(request, 'slow.html')

@csrf_exempt
def webhook_view(request):
    pass
```

### Practical Example: A Complete View

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Book, Author
from .forms import BookForm

def book_list(request):
    search_query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    sort_by = request.GET.get('sort', 'title')

    books = Book.objects.select_related('author', 'publisher').all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query) |
            Q(subtitle__icontains=search_query)
        )
    if genre_filter:
        books = books.filter(genre=genre_filter)

    sort_mapping = {
        'title': 'title', '-title': '-title',
        'newest': '-publication_date', 'oldest': 'publication_date',
        'rating': '-rating', 'popular': '-borrowed_count',
    }
    books = books.order_by(sort_mapping.get(sort_by, 'title'))

    paginator = Paginator(books, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'genre_filter': genre_filter,
        'sort_by': sort_by,
        'genre_choices': Book.GENRE_CHOICES,
    }
    return render(request, 'books/book_list.html', context)

@login_required
def book_detail(request, pk):
    book = get_object_or_404(
        Book.objects.select_related('author', 'publisher').prefetch_related('reviews'),
        pk=pk
    )
    user_review = None
    if request.user.is_authenticated:
        user_review = book.reviews.filter(user=request.user).first()

    similar_books = Book.objects.filter(genre=book.genre).exclude(pk=book.pk).order_by('-rating')[:5]

    context = {'book': book, 'user_review': user_review, 'similar_books':
        similar_books}
    return render(request, 'books/book_detail.html', context)

def book_search_ajax(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    books = Book.objects.filter(
        Q(title__icontains=query) |
        Q(author__first_name__icontains=query) |
        Q(author__last_name__icontains=query)
    )[:10]

    results = [
        {'id': b.id, 'title': b.title, 'author': str(b.author), 'url':
            b.get_absolute_url()}
        for b in books
    ]
    return JsonResponse({'results': results})
```

### Summary

- The Role of Views: how they bridge models and templates.
- The Request-Response Cycle: understanding the flow of a request.
- Function-Based vs. Class-Based Views: when to use each.
- The Request and Response objects, and Django's shortcut functions.
- URL parameters, the url tag, namespacing, and view decorators.
- A complete, real-world view implementation.

## 3.2 Function-Based Views

Function-Based Views (FBVs) are Python functions that take a request object and return a response object — ideal for beginners and situations needing maximum clarity and control.

### The Anatomy of a Function-Based View

```python
from django.http import HttpResponse
from django.shortcuts import render

def my_view(request):
    # 1. Process the request
    # 2. Perform business logic
    # 3. Prepare context data
    # 4. Return a response
    return HttpResponse("Hello, World!")
```

### Handling HTTP Methods

```python
from django.shortcuts import render, redirect

def book_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        # ... process data ...
        return redirect('book-list')
    else:
        return render(request, 'books/create.html')
```

**Restricting allowed methods:**

```python
from django.views.decorators.http import require_http_methods, require_GET, require_POST, require_safe

@require_http_methods(['GET', 'POST'])
def book_create(request):
    pass # Other methods return 405 Method Not Allowed

@require_GET
def book_list(request):
    pass

@require_POST
def book_delete(request, pk):
    pass # Prevents accidental deletions via GET

@require_safe
def book_detail(request, pk):
    pass # Only GET and HEAD
```

**Complete example combining decorators:**

```python
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import BookForm

@login_required
@require_http_methods(['GET', 'POST'])
def book_create(request):
    """Create a new book. GET displays the form, POST processes it."""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, f'Book "{book.title}" created!')
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {'form': form, 'title': 'Create Book'})
```

### Working with GET Parameters

```python
from django.db.models import Q

def book_list(request):
    search_query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')
    sort_by = request.GET.get('sort', 'title')

    books = Book.objects.all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )
    if genre:
        books = books.filter(genre=genre)

    sort_options = {
        'title': 'title', '-title': '-title',
        'newest': '-publication_date', 'oldest': 'publication_date', 'rating': '-rating',
    }
    books = books.order_by(sort_options.get(sort_by, 'title'))

    return render(request, 'books/list.html', {
        'books': books, 'search_query': search_query, 'genre': genre, 'sort_by': sort_by,
    })
```

To preserve query parameters across pagination links, pass `request.GET.urlencode()` into the context.

### Working with POST Parameters

```python
from django.contrib import messages

def book_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author_id = request.POST.get('author')

        if not title or not author_id:
            messages.error(request, 'Title and author are required.')
            return render(request, 'books/create.html', {'errors': True})

        author = get_object_or_404(Author, pk=author_id)
        book = Book.objects.create(
            title=title, author=author,
            publication_date=request.POST.get('publication_date'),
            genre=request.POST.get('genre'), pages=request.POST.get('pages'),
            summary=request.POST.get('summary'),
        )
        messages.success(request, f'Book "{book.title}" created!')
        return redirect('book-detail', pk=book.pk)

    return render(request, 'books/create.html')
```

**Handling file uploads:**

```python
def book_create(request):
    if request.method == 'POST':
        cover_image = request.FILES.get('cover_image')
        if cover_image and cover_image.size > 5 * 1024 * 1024: # 5MB
            messages.error(request, 'File is too large. Max size is 5MB.')
            return render(request, 'books/create.html')

        book = Book.objects.create(
            title=request.POST['title'],
            cover_image=cover_image,
        )
        messages.success(request, f'Book "{book.title}" created!')
        return redirect('book-detail', pk=book.pk)

    return render(request, 'books/create.html')
```

### Handling Forms with Function-Based Views

```python
from .forms import BookForm

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, f'Book "{book.title}" created!')
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm()

    return render(request, 'books/book_form.html', {'form': form, 'title': 'Create Book'})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated!')
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm(instance=book)

    return render(request, 'books/book_form.html', {'form': form, 'book': book,
        'title': 'Update Book'})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" deleted!')
        return redirect('book-list')

    return render(request, 'books/book_confirm_delete.html', {'book': book})
```

### Redirects and Messages

```python
from django.shortcuts import redirect
from django.contrib import messages

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" was created successfully!')
            return redirect('book-detail', pk=book.pk)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'books/book_form.html', {'form': form})
```

```html
<!-- Display messages in the base template -->
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
    {% endfor %}
{% endif %}
```

### Handling AJAX Requests

```python
from django.http import JsonResponse
from django.urls import reverse

def book_search_ajax(request):
    """Search books via AJAX and return JSON."""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__first_name__icontains=query)
    )[:10]

    results = [
        {'id': b.id, 'title': b.title, 'author': str(b.author),
            'url': reverse('book-detail', args=[b.id])}
        for b in books
    ]
    return JsonResponse({'results': results})

def book_toggle_availability(request, pk):
    """Toggle book availability via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    book = get_object_or_404(Book, pk=pk)
    book.is_available = not book.is_available
    book.save()
    return JsonResponse({'success': True, 'is_available': book.is_available})
```

**Partial HTML responses:**

```python
from django.template.loader import render_to_string

def book_list_partial(request):
    books = Book.objects.all()
    html = render_to_string('books/_book_list.html', {'books': books},
        request=request)
    return JsonResponse({'html': html})
```

### Advanced Function-Based View Patterns

**"Fat Models, Thin Views":** keep business logic in models, not views.

```python
# models.py
class Book(models.Model):
    def can_be_borrowed(self):
        return self.is_available and self.copies.filter(is_borrowed=False).exists()

    def borrow(self, user):
        if not self.can_be_borrowed():
            raise ValueError("Book cannot be borrowed")
        # ... borrow logic ...

# views.py
def book_borrow(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method != 'POST':
        return redirect('book-detail', pk=pk)
    try:
        book.borrow(request.user)
        messages.success(request, f'You borrowed "{book.title}"')
    except ValueError as e:
        messages.error(request, str(e))
    return redirect('book-detail', pk=pk)
```

**The Service Layer pattern** for complex business logic:

```python
# services.py
class BookService:
    @staticmethod
    def create_book(data, user):
        book = Book(**data)
        book.created_by = user
        book.full_clean()
        book.save()
        BookService._send_creation_notification(book)
        return book

    @staticmethod
    def _send_creation_notification(book):
        pass

# views.py
from .services import BookService

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = BookService.create_book(form.cleaned_data, request.user)
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})
```

**The Decorator pattern** for reusable view logic:

```python
from functools import wraps

def user_owns_book(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.get('pk')
        book = get_object_or_404(Book, pk=pk)
        if request.user != book.created_by and not request.user.is_superuser:
            messages.error(request, 'You do not own this book.')
            return redirect('book-list')
        kwargs['book'] = book
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@user_owns_book
def book_edit(request, pk, book):
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book-detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'book': book})
```

**Try/except for error handling:**

```python
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError

def book_create(request):
    if request.method == 'POST':
        try:
            book = Book.objects.create(title=request.POST['title'], isbn=request.POST['isbn'])
            return redirect('book-detail', pk=book.pk)
        except IntegrityError:
            messages.error(request, 'A book with this ISBN already exists.')
        except PermissionDenied:
            messages.error(request, 'You do not have permission to create books.')
    return render(request, 'books/create.html')
```

### Performance Optimization for Function-Based Views

```python
def book_list(request):
    books = Book.objects.select_related('author',
        'publisher').prefetch_related('genres')
    return render(request, 'books/list.html', {'books': books})
@cache_page(60 * 15)
@vary_on_headers('User-Agent')
def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/list.html', {'books': books})

from django.utils.functional import cached_property

class Book(models.Model):
    @cached_property
    def related_books(self):
        return Book.objects.filter(genre=self.genre).exclude(pk=self.pk)[:10]
```

### Testing Function-Based Views

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class BookViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title='Test Book', isbn='1234567890123', ...)

    def test_book_list_view(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')

    def test_book_create_view_login_required(self):
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_book_search_ajax(self):
        response = self.client.get(reverse('book-search-ajax'), {'q': 'Test'})
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['results'][0]['title'], 'Test Book')
```

### Common Pitfalls and Best Practices

| Mistake | Fix |
|---|---|
| Mixing POST and GET logic in one view | Separate views for display and creation |
| Not validating user input | Use Django forms, not raw request.POST |
| Not checking permissions | Use login_required / has_perm checks |
| Expensive operations in the view | Move to model properties / background tasks |

### Summary

- The anatomy of an FBV and handling different HTTP methods.
- Working with GET and POST parameters, including file uploads.
- Handling forms, redirects, and messages.
- Handling AJAX requests with JSON and partial HTML responses.
- Advanced patterns: fat models, service layers, custom decorators, try/except.
- Performance optimization, testing, and common pitfalls.

## 3.3 Class-Based Views

Class-Based Views (CBVs) represent Django's object-oriented approach to handling HTTP requests, offering powerful abstractions, inheritance, and code reuse.

### The Philosophy of Class-Based Views

- Code Reuse: inheritance lets you reuse view logic across multiple views.
- Organization: related functionality is grouped together in a class.
- Extensibility: override specific methods without rewriting the entire view.
- DRY Principle: generic views handle common patterns with minimal code.
- Mixins: compose reusable behavior from multiple parent classes.

Use CBVs when you need to reuse view logic, are using Django's generic views, or need mixins. Stick with FBVs for simple, unique views, maximum explicitness, or non-standard method handling.

### The Base View Class

All Class-Based Views inherit from `django.views.generic`.View.

```python
from django.http import HttpResponse
from django.views import View

class MyView(View):
    """A simple class-based view."""
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello from GET!")

    def post(self, request, *args, **kwargs):
        return HttpResponse("Hello from POST!")

# urls.py
from .views import MyView, BookListView, BookDetailView

urlpatterns = [
    path('my-view/', MyView.as_view(), name='my-view'),
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
```

`as_view()` is a class method that creates an instance of the view class and returns a callable. That callable creates a view instance, calls `setup()` to initialize it, then calls `dispatch()` to route the request to the appropriate HTTP method handler.

### Handling HTTP Methods

```python
from django.http import JsonResponse
from django.views import View

class BookAPIView(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        data = [{'id': b.id, 'title': b.title} for b in books]
        return JsonResponse({'books': data})

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        if title:
            book = Book.objects.create(title=title)
            return JsonResponse({'id': book.id, 'title': book.title}, status=201)
        return JsonResponse({'error': 'Title required'}, status=400)

    def put(self, request, *args, **kwargs):
        return JsonResponse({'message': 'PUT not implemented'}, status=405)

    def delete(self, request, *args, **kwargs):
        return JsonResponse({'message': 'DELETE not implemented'}, status=405)
```

### The View Hierarchy

```
View
|-- TemplateView
|-- RedirectView
`-- Generic views (for models)
    |-- ListView
    |-- DetailView
    |-- CreateView
    |-- UpdateView
    |-- DeleteView
    `-- FormView
```

### TemplateView: The Simplest Generic View

```python
from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = 'My Library'
        context['features'] = [
            'Browse thousands of books',
            'Read reviews from other readers',
            'Track your reading progress',
        ]
        return context

class UserProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username') # Captured from URL
        return context

# urls.py
path('profile/<str:username>/', UserProfileView.as_view(), name='profile')
```

### RedirectView: Handling Redirects

```python
from django.views.generic import RedirectView

class OldBookListView(RedirectView):
    url = '/books/'
    permanent = True # 301 redirect

class BookRedirectView(RedirectView):
    permanent = True
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        old_id = kwargs.get('old_id')
        book = get_object_or_404(Book, old_id=old_id)
        return reverse('book-detail', args=[book.id])
```

### Introduction to Generic Display Views

### ListView: Displaying Lists of Objects

```python
from django.views.generic import ListView
from .models import Book

class BookListView(ListView):
    """Display a list of all books."""
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    ordering = ['title']
```

**Customizing the queryset:**

```python
class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('author', 'publisher')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Book.GENRE_CHOICES
        context['total_books'] = self.get_queryset().count()
        return context
```

### DetailView: Displaying Individual Objects

```python
from django.views.generic import DetailView

class BookDetailView(DetailView):
    """Display detailed information about a book."""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('author',
            'publisher').prefetch_related('reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['similar_books'] = Book.objects.filter(genre=book.genre).exclude(pk=book.pk).order_by('-rating')[:5]
        return context
```

### Generic Edit Views

Django provides four generic edit views: CreateView, UpdateView, DeleteView, and FormView (covered in full detail in the next section).

```python
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Book "{self.object.title}" was created!')
        return response

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'

    def get_success_url(self):
        return reverse('book-detail', args=[self.object.pk])

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')
```

### FormView

```python
from django.views.generic.edit import FormView
from .forms import ContactForm

class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact-success')

    def form_valid(self, form):
        # form.cleaned_data contains the form data
        return super().form_valid(form)
```

### Using Mixins

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

class UserBookListView(LoginRequiredMixin, ListView):
    model = Book
    def get_queryset(self):
        return Book.objects.filter(created_by=self.request.user)

class StaffBookCreateView(PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    permission_required = 'books.add_book'
    raise_exception = True

class OwnerEditView(UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm

    def test_func(self):
        book = self.get_object()
        return self.request.user == book.created_by or self.request.user.is_staff
```

**Creating custom mixins:**

```python
# mixins.py
class MessageSuccessMixin:
    success_message = None

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message % self.object.__dict__)
        return response

class RedirectToDetailMixin:
    def get_success_url(self):
        return reverse('book-detail', args=[self.object.pk])

# Composing mixins
class BookCreateView(LoginRequiredMixin, MessageSuccessMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_message = 'Book "%(title)s" was created!'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
```

### Advanced Class-Based View Techniques

**`dispatch()`** for logic that runs before any HTTP method:

```python
class MyView(View):
    def dispatch(self, request, *args, **kwargs):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'bot' in user_agent.lower():
            return HttpResponse('Not allowed', status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("Hello, World!")
```

**`setup()`** for initializing attributes before `dispatch()`:

```python
class BookView(View):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.book = None
        self.user = request.user
```

### Testing Class-Based Views

```python
class BookListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title='Test Book', ...)

    def test_list_view(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_list.html')

    def test_list_view_pagination(self):
        for i in range(25):
            Book.objects.create(title=f'Book {i}', ...)
        response = self.client.get(reverse('book-list'))
        self.assertEqual(len(response.context['books']), 20)
        self.assertTrue(response.context['is_paginated'])
```

### Best Practices for Class-Based Views

- Keep views thin — move business logic to models or services.
- Use generic views when possible; they handle common patterns with minimal code.
- Override methods (`get_queryset()`, `get_context_data()`) rather than setting attributes for dynamic behavior.
- Use mixins for reusable logic, and always call `super()` when overriding methods.
- Be explicit with method names: `get()` for GET, `post()` for POST, etc.
- Use `reverse_lazy()` for URLs in class attributes to avoid circular imports.
- Handle permissions with LoginRequiredMixin, PermissionRequiredMixin, or UserPassesTestMixin.

### Common Pitfalls

| Pitfall | Solution |
|---|---|
| Overcomplicating simple views | Use Function-Based Views for simple cases |
| Not calling `super()` | Always call `super()` in overridden methods |
| Using `reverse()` in class attributes | Use `reverse_lazy()` instead |
| Forgetting `.as_view()` when registering CBVs | Remember it in urls.py |
| Mixin order issues | Place mixins before the base view class |

### Summary

- The base View class, `as_view()`, and HTTP method handling.
- TemplateView and RedirectView for simple templates and redirects.
- Generic display views: ListView and DetailView.
- Generic edit views: CreateView, UpdateView, DeleteView, FormView.
- Mixins for composing reusable behavior.
- Advanced techniques: custom dispatch, setup, testing, and best practices.

## 3.4 Generic Display Views

Generic display views are the workhorses of Django's class-based view system, handling the most common patterns: displaying lists of objects and detailed information about individual objects.

### ListView: Displaying Lists of Objects

**Minimal configuration:**

```python
from django.views.generic import ListView
from .models import Book

class BookListView(ListView):
    model = Book
```

This single line creates a fully functional list view. Django automatically uses the template books/book_list.html, the context variable object_list, and returns all objects from the model.

**Explicit configuration:**

```python
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    ordering = ['title']
    queryset = Book.objects.filter(is_available=True)
```

### Customizing the Queryset

```python
class BookListView(ListView):
    model = Book
    context_object_name = 'books'

    def get_queryset(self):
        """Return only available books."""
        return Book.objects.filter(is_available=True)
```

**Dynamic filtering based on URL parameters:**

```python
class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.kwargs.get('genre')
        author_id = self.kwargs.get('author_id')
        if genre:
            queryset = queryset.filter(genre=genre)
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        return queryset

# urls.py
path('books/genre/<str:genre>/', BookListView.as_view(), name='books-by-genre')
```

**Search functionality with GET parameters:**

```python
from django.db.models import Q

class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__last_name__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
```

**Sorting and filtering together:**

```python
class BookListView(ListView):
    model = Book
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        genre = self.request.GET.get('genre')
        sort_by = self.request.GET.get('sort', 'title')
        search_query = self.request.GET.get('q')

        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query))
        if genre:
            queryset = queryset.filter(genre=genre)

        sort_mapping = {
            'title': 'title', '-title': '-title',
            'newest': '-publication_date', 'oldest': 'publication_date',
            'rating': '-rating', 'popular': '-borrowed_count',
        }
        queryset = queryset.order_by(sort_mapping.get(sort_by, 'title'))
        queryset = queryset.select_related('author', 'publisher')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_params'] = self.request.GET.urlencode()
        context['genre'] = self.request.GET.get('genre', '')
        context['sort_by'] = self.request.GET.get('sort', 'title')
        return context
```

### Advanced Pagination

```python
from django.core.paginator import Paginator

class BookListView(ListView):
    model = Book
    paginate_by = 20

    def get_paginator(self, queryset, per_page, orphans=0,
        allow_empty_first_page=True):
        """Custom paginator with orphan handling."""
        return Paginator(queryset, per_page, orphans=5,
            allow_empty_first_page=allow_empty_first_page)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context['page_obj']
        context['total_pages'] = page_obj.paginator.num_pages
        context['total_objects'] = page_obj.paginator.count
        return context
```

**Letting users select items per page:**

```python
class BookListView(ListView):
    model = Book
    paginate_by = 20

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page')
        if per_page in ['10', '20', '50', '100']:
            return int(per_page)
        return self.paginate_by
```

### Customizing Context Data

```python
class BookListView(ListView):
    model = Book
    context_object_name = 'books'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        context['available_books'] = Book.objects.filter(is_available=True).count()
        context['featured_books'] = Book.objects.filter(rating__gte=4)[:5]
        context['genre_choices'] = Book.GENRE_CHOICES
        return context
```

**Passing data from the URL:**

```python
class AuthorBookListView(ListView):
    model = Book
    template_name = 'books/author_books.html'
    context_object_name = 'books'

    def get_queryset(self):
        self.author = get_object_or_404(Author, pk=self.kwargs['author_id'])
        return Book.objects.filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context
```

### Template Rendering and Performance

```python
class BookListView(ListView):
    model = Book

    def get_template_names(self):
        """Dynamically choose template based on context."""
        if self.request.GET.get('layout') == 'grid':
            return ['books/book_grid.html']
        return ['books/book_list.html']

    def get_queryset(self):
        """Optimize queries."""
        return super().get_queryset().select_related(
            'author', 'publisher'
        ).prefetch_related('reviews', 'genres')
```

### DetailView: Displaying Individual Objects

**Minimal configuration:**

```python
from django.views.generic import DetailView
from .models import Book

class BookDetailView(DetailView):
    model = Book
```

Django automatically uses books/book_detail.html, the context variable object, and looks up the object by pk or slug from the URL.

**Using slug instead of pk:**

```python
class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

# urls.py
path('books/<slug:slug>/', BookDetailView.as_view(), name='book-detail')
```

**Custom object retrieval with 404 handling:**

```python
from django.shortcuts import get_object_or_404
from django.http import Http404

class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        if not queryset.exists():
            raise Http404("No book found with the given ID.")
        return queryset.first()
```

### Customizing Context Data

```python
class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        context['similar_books'] = Book.objects.filter(
            genre=book.genre
        ).exclude(pk=book.pk).order_by('-rating')[:5]

        context['author_books'] = Book.objects.filter(
            author=book.author
        ).exclude(pk=book.pk).order_by('-publication_date')[:5]

        if self.request.user.is_authenticated:
            context['user_review'] = book.reviews.filter(user=self.request.user).first()

        reviews = book.reviews.all()
        if reviews:
            context['avg_rating'] = sum(r.rating for r in reviews) / len(reviews)
            context['review_count'] = len(reviews)

        return context
```

**Dynamic title and meta data for SEO:**

```python
class BookDetailView(DetailView):
    model = Book
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['page_title'] = f"{book.title} - Our Library"
        context['meta_description'] = book.summary[:150]
        context['og_image'] = book.cover_image.url if book.cover_image else None
        return context
```

### Lazy Loading Optimization

```python
class BookDetailView(DetailView):
    model = Book

    def get_queryset(self):
        """Preload related data to avoid N+1 queries."""
        return super().get_queryset().select_related(
            'author', 'publisher'
        ).prefetch_related(
            'reviews', 'reviews__user', 'genres', 'copies', 'authors'
        )
```

### Advanced Display Patterns

**Combining ListView and DetailView in one FBV:**

```python
class BookCatalogView(View):
    """Display both a list and a featured book detail."""
    def get(self, request, *args, **kwargs):
        books = Book.objects.select_related('author').all()
        featured = Book.objects.filter(is_featured=True).first()
        return render(request, 'books/catalog.html', {'books': books, 'featured':
            featured})
```

**Context processors for global data:**

```python
# context_processors.py
def site_globals(request):
    return {
        'site_name': 'My Library',
        'year': timezone.now().year,
        'contact_email': 'info@mylibrary.com',
    }
```

### Testing Generic Display Views

```python
class BookListViewTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Test', last_name='Author')
        self.book = Book.objects.create(title='Test Book', author=self.author, ...)

    def test_list_view_renders_correct_template(self):
        response = self.client.get(reverse('book-list'))
        self.assertTemplateUsed(response, 'books/book_list.html')

    def test_list_view_pagination(self):
        for i in range(25):
            Book.objects.create(title=f'Book {i}', author=self.author, ...)
        response = self.client.get(reverse('book-list'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['books']), 20)

class BookDetailViewTests(TestCase):
    def test_detail_view_404_for_nonexistent_book(self):
        response = self.client.get(reverse('book-detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_optimizes_queries(self):
        with self.assertNumQueries(2):
            self.client.get(reverse('book-detail', args=[self.book.pk]))
```

### Common Pitfalls and Best Practices Summary

| Pitfall | Solution |
|---|---|
| N+1 query problem | Use `select_related()` / `prefetch_related()` in `get_queryset()` |
| Forgetting to call `super()` | Always call `super()` when overriding methods |
| Not handling empty QuerySets | Use {% empty %} in templates or get_object_or_404 |
| Missing context_object_name | Set it for clearer template variable names |
| Hard-coding template paths | Use template_name or `get_template_names()` |

- Always optimize querysets with `select_related()` and `prefetch_related()`.
- Use context_object_name for readable templates.
- Keep views thin; move complex logic to models or services.
- Set paginate_by and provide navigation in templates.
- Cache expensive views with cache_page where appropriate.
- Handle 404s gracefully with get_object_or_404.

### Summary

- ListView: customization, filtering, search, and pagination.
- DetailView: related data, extra context, and SEO metadata.
- Advanced patterns: combining views, nested contexts, global data via context processors.
- Performance optimization with `select_related()`, `prefetch_related()`, and caching.
- Testing strategies and best practices for maintainable display views.

## 3.5 Generic Edit Views

Generic edit views are the counterpart to display views, handling the most common data modification patterns: creating, updating, deleting, and processing forms.

| View | Purpose | Typical Use Case |
|---|---|---|
| CreateView | Create new objects | Add a new book, register a user |
| UpdateView | Update existing objects | Edit a book's details, update a profile |
| DeleteView | Delete objects | Remove a book, delete a user account |
| FormView | Display and process forms | Contact forms, search forms |

All these views share a common pattern: display a form on GET, process submission on POST, validate the data, perform an action on success, and redirect on success or re-render on error.

### CreateView: Creating New Objects

**Minimal configuration:**

```python
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Book
from .forms import BookForm

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')
```

**Customizing the form with `get_form()`:**

```python
class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['title'].widget.attrs.update({'class': 'form-control'})
        form.fields['rating'].widget = forms.HiddenInput()
        return form
```

**Setting automatic fields and additional processing:**

```python
class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')

    def form_valid(self, form):
        """Save the book with additional processing."""
        book = form.save(commit=False)
        book.created_by = self.request.user
        book.is_available = True

        from django.utils.text import slugify
        book.slug = slugify(book.title)

        book.save()
        form.save_m2m()
        self._send_notification(book)
        return super().form_valid(form)

    def _send_notification(self, book):
        pass
```

### UpdateView: Updating Existing Objects

```python
from django.views.generic.edit import UpdateView

class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book-list')
```

**Limiting access to the user's own objects:**

```python
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse('book-detail', args=[self.object.pk])
```

**Custom object retrieval with permission checks:**

```python
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.has_perm('books.change_book'):
            if obj.created_by != self.request.user:
                raise PermissionDenied("You don't have permission to edit this book.")
        return obj
```

**Pre-populating a form with computed data:**

```python
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm

    def get_initial(self):
        initial = super().get_initial()
        book = self.get_object()
        initial['age'] = book.age
        initial['last_updated_by'] = self.request.user.username
        return initial
```

### DeleteView: Deleting Objects

```python
from django.views.generic.edit import DeleteView

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')
```

**Adding success messages and confirmation context:**

```python
class BookDeleteView(DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        book_title = self.object.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Book "{book_title}" was deleted successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context['related_objects'] = {
            'reviews': book.reviews.count(),
            'copies': book.copies.count(),
        }
        return context
```

**Protecting against deletion:**

```python
from django.db.models import ProtectedError

class BookDeleteView(DeleteView):
    model = Book
    success_url = reverse_lazy('book-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().delete(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, f'Cannot delete "{self.object.title}" — it has related objects.')
            return redirect('book-detail', pk=self.object.pk)
```

**Permission handling:**

```python
class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book-list')
    permission_required = 'books.delete_book'
    raise_exception = True
```

### FormView: Working with Forms

FormView is the most generic of the edit views — it doesn't work with a model directly but handles any form.

```python
from django.views.generic.edit import FormView
from .forms import ContactForm

class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = reverse_lazy('contact-success')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        from django.core.mail import send_mail
        send_mail(f'Contact Form', f'From: {name} <{email}>\n\n{message}',
            email, ['info@example.com'], fail_silently=False)

        messages.success(self.request, 'Your message has been sent!')
        return super().form_valid(form)
```

**Multi-step form (wizard) pattern:**

```python
class Step1Form(forms.Form):
    title = forms.CharField(max_length=200)
    author = forms.CharField(max_length=100)

class WizardView(FormView):
    form_class = Step1Form
    template_name = 'wizard/step1.html'
    success_url = reverse_lazy('wizard-step2')

    def form_valid(self, form):
        """Store data and move to next step."""
        self.request.session['step1_data'] = form.cleaned_data
        return super().form_valid(form)
```

### Combining Edit Views with Mixins

```python
class SuccessMessageMixin:
    success_message = None
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message % self.object.__dict__)
        return response

class OwnerCheckMixin:
    owner_field = 'created_by'
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and getattr(obj, self.owner_field) != self.request.user:
            messages.error(self.request, 'You do not have permission to edit this object.')
            return redirect('book-list')
        return obj

class BookUpdateView(
    LoginRequiredMixin, OwnerCheckMixin, SuccessMessageMixin, UpdateView
):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_message = 'Book "%(title)s" was updated!'
    owner_field = 'created_by'
```

### Handling AJAX with Edit Views

```python
from django.http import JsonResponse
from django.views.generic.edit import CreateView

class BookCreateAjaxView(CreateView):
    model = Book
    form_class = BookForm

    def form_valid(self, form):
        book = form.save(commit=False)
        book.created_by = self.request.user
        book.save()
        form.save_m2m()
        return JsonResponse({'success': True, 'id': book.id, 'title': book.title})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
```

### Testing Generic Edit Views

```python
class BookCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.author = Author.objects.create(first_name='Test', last_name='Author')
        self.client.login(username='testuser', password='testpass')

    def test_create_view_creates_object(self):
        data = {'title': 'New Book', 'author': self.author.id, 'isbn': '9781234567890',
            ...}
        response = self.client.post(reverse('book-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_create_view_invalid_data(self):
        data = {'title': '', 'author': self.author.id}
        response = self.client.post(reverse('book-create'), data)
        self.assertEqual(response.status_code, 200) # Re-render with errors
```

### Common Pitfalls and Best Practices

| Pitfall | Solution |
|---|---|
| Not setting success_url | Always set success_url or override `get_success_url()` |
| Using `reverse()` instead of `reverse_lazy()` | Use `reverse_lazy()` for class attributes |
| Forgetting to set created_by | Override `form_valid()` to set automatic fields |
| Not handling file uploads | Set enctype and handle request.FILES |
| Not providing feedback | Use messages for success/failure |

### Summary

- CreateView, UpdateView, DeleteView, and FormView, and their common patterns.
- Customizing form handling, automatic fields, and success messages.
- Permission checks, versioning, and partial updates.
- Multi-step forms, mixins, and AJAX handling.
- Testing strategies and common pitfalls to avoid.

## 3.6 Template Fundamentals

Templates are the presentation layer of your Django application, transforming view data into HTML that users can interact with, while enforcing a clean separation between presentation and business logic.

### The Role of Templates

**What Templates Do:** display data from context, provide structure and layout, enforce consistency, and enable reusability through inheritance and includes.

**What Templates Should NOT Do:** complex business logic, direct database access, or modify data.

### Template Configuration

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

Templates are loaded first from DIRS (project-level), then from app directories when APP_DIRS is True.

```
myproject/
├── templates/                  # Project-level templates
│   ├── base.html
│   └── 404.html
├── books/
│   ├── templates/
│   │   └── books/              # App-namespaced directory
│   │       ├── book_list.html
│   │       ├── book_detail.html
│   │       └── book_form.html
│   └── models.py
└── manage.py
```

### Template Variables

```html
<h1>{{ book.title }}</h1>
<p>Author: {{ book.author.first_name }} {{ book.author.last_name }}</p>
<p>Published: {{ book.publication_date }}</p>

<!-- Method calls (without arguments) -->
<p>{{ book.full_title }}</p>
<p>{{ book.age }} years old</p>

<!-- List indexing -->
<p>First author: {{ authors.0.full_name }}</p>

<!-- Safely access variables that might not exist -->
<p>{{ book|default:"No book" }}</p>
```

Variable resolution order: dictionary lookup, attribute lookup, list-index lookup, then method call. If none work, Django returns an empty string — no error.

### Template Filters

```html
<p>{{ book.title|upper }}</p>
<p>{{ book.title|title }}</p>
<p>{{ book.title|truncatechars:50 }}</p>
<p>{{ book.summary|truncatewords:30 }}</p>
<p>{{ book.subtitle|default:"No subtitle" }}</p>
<p>{{ genres|join:", " }}</p>
<p>{{ authors|length }}</p>
<p>{{ book.publication_date|date:"F j, Y" }}</p>
<p>{{ book.publication_date|timesince }}</p>
<p>{{ book.pages|add:100 }}</p>
<p>{{ book.rating|floatformat:1 }}</p>
<p>{{ book.summary|linebreaks }}</p>

<!-- Chaining filters -->
<p>{{ book.title|truncatewords:5|upper }}</p>
```

| Category | Filters |
|---|---|
| String | upper, lower, title, capfirst, truncatechars, truncatewords, slugify |
| Default | default, default_if_none, yesno |
| List | join, length, slice, first, last, dictsort |
| Date/Time | date, time, timesince, timeuntil |
| Number | add, floatformat, filesizeformat |
| HTML | linebreaks, linebreaksbr, escape, safe, urlize |

### Template Tags

**Conditional tags:**

```html
{% if user.is_authenticated %}
    <p>Welcome back, {{ user.username }}!</p>
{% else %}
    <p>Please <a href="{% url 'login' %}">log in</a>.</p>
{% endif %}

{% if book.rating >= 4 %}
    <span class="badge badge-success">Highly Rated!</span>
{% elif book.rating >= 3 %}
    <span class="badge badge-warning">Good</span>
{% else %}
    <span class="badge badge-secondary">Average</span>
{% endif %}
```

**Loop tags:**

```html
<ul>
    {% for book in books %}
        <li><a href="{% url 'book-detail' book.id %}">{{ book.title }}</a></li>
    {% empty %}
        <li>No books found.</li>
    {% endfor %}
</ul>

{% for book in books %}
    <tr>
        <td>{{ forloop.counter }}</td> <!-- 1, 2, 3... -->
        <td>{{ forloop.first }}</td> <!-- True if first -->
        <td>{{ forloop.last }}</td> <!-- True if last -->
        <td>{{ book.title }}</td>
    </tr>
{% endfor %}
```

**URL and static tags:**

```html
<a href="{% url 'book-detail' book.id %}">View Book</a>
<a href="{% url 'books:book-detail' book.id %}">View Book</a>

{% load static %}
<img src="{% static 'images/logo.png' %}" alt="Logo">
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

**Other useful tags:**

```html
{% with total=books|length %}
    <p>Total books: {{ total }}</p>
{% endwith %}

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{% comment %}
    A multi-line comment; does not appear in rendered HTML.
{% endcomment %}

<p>Current year: {% now "Y" %}</p>
```

### Template Inheritance

**base.html (the parent template):**

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>{% block title %}My Library{% endblock %}</title>
        {% block css %}
            <link rel="stylesheet" href="{% static 'css/base.css' %}">
        {% endblock %}
    </head>
    <body>
        <nav>
            <ul>
                <li><a href="{% url 'home' %}">Home</a></li>
                <li><a href="{% url 'book-list' %}">Books</a></li>
            </ul>
        </nav>

        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}

        <main>
            {% block content %}
            {% endblock %}
        </main>

        <footer><p>&copy; {% now "Y" %} My Library</p></footer>

        {% block javascript %}
            <script src="{% static 'js/base.js' %}"></script>
        {% endblock %}
    </body>
</html>
```

**A child template extending it:**

```html
{% extends 'base.html' %}

{% block title %}Book List - My Library{% endblock %}

{% block content %}
    <h1>Book List</h1>
    <div class="book-grid">
        {% for book in books %}
            <div class="book-card">
                <a href="{% url 'book-detail' book.id %}">
                    <h3>{{ book.title }}</h3>
                    <p>{{ book.author }}</p>
                </a>
            </div>
        {% empty %}
            <p>No books found.</p>
        {% endfor %}
    </div>
{% endblock %}

{% block javascript %}
    {{ block.super }}
    <script src="{% static 'js/books.js' %}"></script>
{% endblock %}
```

{{ block.super }} includes the parent block's content — useful for appending, rather than replacing, a block.

### Template Includes

```html
<!-- Simple include -->
{% include 'includes/pagination.html' %}

<!-- Include with variables -->
{% include 'includes/book_card.html' with book=book %}

<!-- Include with specific variables only -->
{% include 'includes/book_card.html' with book=book only %}

<!-- includes/book_card.html -->
<div class="book-card">
    <a href="{% url 'book-detail' book.id %}">
        <h3 class="book-title">{{ book.title|truncatewords:5 }}</h3>
        <p class="book-author">{{ book.author }}</p>
        <p class="book-rating">★ {{ book.rating }}/5</p>
    </a>
</div>
```

### Context Processors

Context processors add data to the context of every template automatically.

```python
# context_processors.py
from .models import Genre

def site_globals(request):
    return {
        'site_name': 'My Library',
        'genres': Genre.objects.all(),
        'current_year': timezone.now().year,
    }

# settings.py
TEMPLATES = [{'OPTIONS': {'context_processors': [
    # ... built-in processors ...
    'myapp.context_processors.site_globals',
]}}]
```

### Working with Forms in Templates

```html
<form method="post" action="{% url 'book-create' %}" enctype="multipart/form-data">
    {% csrf_token %}

    {{ form.as_p }} <!-- Automatic rendering -->

    <!-- Or loop through fields manually -->
    {% for field in form %}
        <div class="form-group">
            {{ field.label_tag }}
            {{ field }}
            {% if field.help_text %}<small>{{ field.help_text }}</small>{% endif %}
            {{ field.errors }}
        </div>
    {% endfor %}

    <button type="submit">Submit</button>
</form>
```

### Working with Static Files

```python
# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

### Best Practices for Templates

- Use template inheritance — don't repeat yourself.
- Keep templates simple; logic belongs in views and models.
- Use {% include %} for reusable components (pagination, cards, forms).
- Escape user-generated content; use |safe only when you're certain it's safe.
- Use {% with %} to assign complex expressions to readable variables.
- Always use {% url %} instead of hard-coding URLs.
- Optimize static files: minify CSS/JS in production.

### Common Template Mistakes

| Mistake | Solution |
|---|---|
| Hard-coding URLs | Use {% url %} tag instead |
| Not escaping user content | Use \|escape or \|safe carefully |
| Complex logic in templates | Move logic to views or custom template tags |
| Duplicating template code | Use inheritance and includes |
| Missing {% csrf_token %} in forms | Always include it in POST forms |
| Forgetting {% load static %} | Load it at the top of the template |

### Summary

- How Django locates and loads templates.
- Template variables, filters, and tags for logic and control flow.
- Template inheritance and includes for maintainable hierarchies.
- Context processors for global data across every template.
- Rendering forms and working with static files in templates.
- Best practices for clean, maintainable templates.

## 3.7 Advanced Template Features

Django's templating language is powerful out of the box, but its true strength lies in its extensibility. Custom template tags and filters let you encapsulate complex logic and keep templates clean and maintainable.

### Custom Template Filters

Custom filters are Python functions that take one or two arguments and return a value.

**Step 1 — Create the filter file:**

```
books/
├── templatetags/          # Create this directory
│   ├── __init__.py
│   └── book_filters.py    # Our custom filters
├── models.py
└── views.py
```

**Step 2 — Write the filter:**

```python
# books/templatetags/book_filters.py
from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='truncate_chars')
def truncate_chars(value, max_length=50):
    """Truncate a string to a specified number of characters."""
    if not value:
        return ''
    if len(value) <= max_length:
        return value
    return value[:max_length].rsplit(' ', 1)[0] + '...'

@register.filter(name='stars')
def stars(rating, max_stars=5):
    """Convert a numeric rating to star symbols."""
    if not rating:
        return ''
    full_stars = int(rating)
    empty_stars = max_stars - full_stars
    return mark_safe('★' * full_stars + '☆' * empty_stars)
```


```python
@register.filter(name='reading_time')
def reading_time(text, words_per_minute=200):
    """Estimate reading time based on word count."""
    if not text:
        return '0 min'
    word_count = len(re.findall(r'\w+', text))
    minutes = max(1, int(word_count / words_per_minute))
    return f'{minutes} min read'
```

**Step 3 — Load and use the filter in templates:**

```html
{% load book_filters %}

<h1>{{ book.title|truncate_chars:30 }}</h1>
<p>{{ book.summary|reading_time:150 }}</p>
<p>Rating: {{ book.rating|stars }}</p>
```

**Filters with multiple arguments:**

```python
@register.filter(name='format_currency')
def format_currency(value, currency_symbol='$', decimal_places=2):
    """Format a number as currency."""
    try:
        value = float(value)
        return mark_safe(f'{currency_symbol}{value:,.{decimal_places}f}')
    except (ValueError, TypeError):
        return value
```

```html
<p>Price: {{ book.price|format_currency:"€":2 }}</p>
<p>Price: {{ book.price|format_currency }}</p> <!-- Defaults: $, 2 decimals -->
```

### Custom Template Tags

Custom template tags are more powerful than filters — they can access the context, render templates, and perform complex operations.

**Simple tags** — the easiest to write, taking arguments and returning a value:

```python
# books/templatetags/book_tags.py
from django import template
from django.utils import timezone
from ..models import Book

register = template.Library()

@register.simple_tag
def current_year():
    """Return the current year."""
    return timezone.now().year

@register.simple_tag(takes_context=True)
def current_url_name(context):
    """Return the name of the current URL."""
    request = context.get('request')
    if request and hasattr(request, 'resolver_match'):
        return request.resolver_match.url_name
    return ''

@register.simple_tag
def get_random_books(count=3):
    """Return a random selection of books."""
    return Book.objects.order_by('?')[:count]
```

```html
{% load book_tags %}

<footer><p>&copy; {% current_year %} My Library</p></footer>
<p>Current page: {% current_url_name %}</p>

<div class="random-books">
    {% get_random_books 5 as random_books %}
    {% for book in random_books %}
        <p>{{ book.title }}</p>
    {% endfor %}
</div>
```

Note: simple_tag supports assigning its result to a variable with "as" — the older @register.assignment_tag decorator was removed in Django 2.0 and simple_tag now covers that use case.

**Inclusion tags** — render a template fragment with provided context, perfect for reusable components:

```python
@register.inclusion_tag('includes/book_card.html')
def book_card(book, show_actions=True):
    """Render a book card component."""
    return {
        'book': book,
        'show_actions': show_actions,
    }

@register.inclusion_tag('includes/author_card.html')
def author_card(author, show_books=True):
    """Render an author card component."""
    return {
        'author': author,
        'book_count': author.books.count(),
        'show_books': show_books,
        'recent_books': author.books.order_by('-publication_date')[:3],
    }
```

```html
{% load book_tags %}

<div class="book-grid">
    {% for book in books %}
        {% book_card book %}
    {% endfor %}
</div>
```

**Using simple_tag with "as" for assignment** (the modern replacement for assignment_tag):

```python
@register.simple_tag
def get_books_by_genre(genre, limit=None):
    """Get books by genre."""
    books = Book.objects.filter(genre=genre)
    if limit:
        books = books[:limit]
    return books
```

```html
{% load book_tags %}

{% get_books_by_genre 'F' 5 as fiction_books %}
<ul>
    {% for book in fiction_books %}
        <li>{{ book.title }}</li>
    {% endfor %}
</ul>
```

**Block tags** — the most complex custom tags, with start and end tags processing enclosed content:

```python
@register.tag(name='capture_as')
def do_capture_as(parser, token):
    """Capture block content into a variable."""
    try:
        tag_name, variable_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            f"{token.contents.split()[0]} tag requires a variable name"
        )
    nodelist = parser.parse(('endcapture_as',))
    parser.delete_first_token()
    return CaptureNode(nodelist, variable_name)

class CaptureNode(template.Node):
    def __init__(self, nodelist, variable_name):
        self.nodelist = nodelist
        self.variable_name = variable_name

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.variable_name] = output
        return ''
```

```html
{% load book_tags %}

{% capture_as book_summary %}
<h2>Summary</h2>
<p>{{ book.summary }}</p>
{% endcapture_as %}

{{ book_summary }}
```

### Context Processors

Context processors add data to the context of every template automatically — ideal for site-wide settings, navigation, and user information.

```python
# books/context_processors.py
from django.utils import timezone
from .models import Genre, Book

def site_settings(request):
    """Add site-wide settings to all templates."""
    return {
        'SITE_NAME': 'My Library',
        'SITE_DESCRIPTION': 'Your premier online library',
        'YEAR': timezone.now().year,
    }

def navigation(request):
    """Add navigation data to all templates."""
    return {
        'nav_genres': Genre.objects.filter(is_active=True),
        'nav_books': Book.objects.filter(is_featured=True)[:5],
    }

def user_data(request):
    """Add user-related data to all templates."""
    if request.user.is_authenticated:
        return {
            'user_books': Book.objects.filter(created_by=request.user)[:5],
            'user_reviews': request.user.reviews.count(),
        }
    return {}

# settings.py
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'books.context_processors.site_settings',
            'books.context_processors.navigation',
            'books.context_processors.user_data',
        ],
    },
}]
```

```html
<!-- These variables are now available in every template -->
<title>{{ SITE_NAME }} - {% block title %}{% endblock %}</title>

{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}</p>
    <p>You have {{ user_books|length }} books in your library</p>
{% endif %}
```

### Template Caching

Caching template fragments can dramatically improve performance for expensive operations.

```html
{% load cache %}

<!-- Cache a fragment for 15 minutes, keyed by book.id -->
{% cache 900 book_card book.id %}
    <div class="book-card">
        <h3>{{ book.title }}</h3>
        <p>Author: {{ book.author }}</p>
    </div>
{% endcache %}
```

**Caching with multiple keys** (e.g. depending on both user and book):

```html
{% cache 600 book_detail user.id book.id %}
    <div class="book-detail">
        <h1>{{ book.title }}</h1>
        {% if user.is_authenticated %}
            <a href="{% url 'book-borrow' book.id %}">Borrow</a>
        {% endif %}
    </div>
{% endcache %}
```

**Versioning the cache key** for controlled invalidation on deploy:

```html
{% cache 3600 book_list_v2 %}
    <div class="book-grid">
        {% for book in books %}
            {% include 'includes/book_card.html' with book=book %}
        {% endfor %}
    </div>
{% endcache %}
```

### Custom Template Loaders

Template loaders determine how Django finds and loads templates. A custom loader can, for example, load templates stored in the database.

```python
# loaders.py
from django.template import TemplateDoesNotExist
from django.template.loaders.base import Loader
from .models import Template as TemplateModel

class DatabaseTemplateLoader(Loader):
    """Load templates from the database."""

    def get_contents(self, origin):
        try:
            template_obj = TemplateModel.objects.get(name=origin.template_name)
            return template_obj.content
        except TemplateModel.DoesNotExist:
            raise TemplateDoesNotExist(origin)

    def get_template_sources(self, template_name):
        yield self.engine.origin(template_name=template_name, loader=self,
            name=template_name)
```

### Template Performance Optimization

```python
# settings.py — precompile and cache parsed templates
TEMPLATES = [{
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
    },
}]
```

- Use block tags efficiently and avoid deeply nested blocks.
- Prefer inclusion tags over {% include %} for complex, frequently-used components.
- Cache expensive template fragments with {% cache %}.

### Summary

- Custom Filters: reusable data transformation functions.
- Custom Tags: simple tags (including 'as' assignment), inclusion tags, and block tags.
- Context Processors for global data across every template.
- Template Caching for performance, and custom template loaders for advanced sourcing.
- Basic performance optimization techniques for templates.

## 3.8 Forms in Django

Forms are the primary way users interact with your web applications, enabling data entry, search, and filtering. Django's form system provides a robust framework for rendering, validation, and processing.

### The Role of Forms in Django

- Rendering: generating HTML form elements.
- Validation: ensuring user input meets your requirements.
- Processing: handling form data and performing actions.

**Key Concepts:** Form (defines fields and validation rules), Field (a single input with validation), Widget (the HTML representation of a field), Bound form (has data attached), Unbound form (empty).

### Creating Basic Forms

```python
# books/forms.py
from django import forms

class BookSearchForm(forms.Form):
    """Form for searching books."""
    query = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search books...'})
    )
    genre = forms.ChoiceField(
        choices=[('', 'All Genres')], # extend with Book.GENRE_CHOICES at runtime
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_rating = forms.IntegerField(
        required=False, min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min rating'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('title', 'Title (A-Z)'), ('-title', 'Title (Z-A)'),
            ('-rating', 'Highest Rated'), ('-publication_date', 'Newest'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
```

### Form Fields

```python
class ContactForm(forms.Form):
    """Example contact form demonstrating various field types."""
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':
        'form-control'}))
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    priority = forms.ChoiceField(choices=[('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High')])
    subscribe = forms.BooleanField(required=False, label="Subscribe to newsletter")
    preferred_contact_date = forms.DateField(required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    attachment = forms.FileField(required=False)
    website = forms.URLField(required=False)
    rating = forms.IntegerField(required=False, min_value=1, max_value=5)
```

| Field Type | Default Widget |
|---|---|
| CharField | TextInput |
| EmailField | EmailInput |
| URLField | URLInput |
| IntegerField / FloatField / DecimalField | NumberInput |
| DateField / DateTimeField / TimeField | DateInput / DateTimeInput / TimeInput |
| BooleanField | CheckboxInput |
| ChoiceField / MultipleChoiceField | Select / SelectMultiple |
| ModelChoiceField / ModelMultipleChoiceField | Select / SelectMultiple |
| FileField / ImageField | FileInput |

### Field Validation

```python
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, FileExtensionValidator

class BookForm(forms.Form):
    title = forms.CharField(
        max_length=200, min_length=3, required=True,
        error_messages={'required': 'Please enter a title.'}
    )
    isbn = forms.CharField(
        max_length=13, min_length=10, required=True,
        validators=[RegexValidator(regex=r'^[0-9-]+$', message='ISBN must contain only numbers and hyphens.')]
    )
    pages = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(10000)]
    )
    cover_image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png',
            'gif'])]
    )

    def clean_isbn(self):
        """Custom validation for a single field."""
        isbn = self.cleaned_data.get('isbn')
        cleaned_isbn = isbn.replace('-', '').replace(' ', '')
        if len(cleaned_isbn) not in [10, 13]:
            raise forms.ValidationError('ISBN must be 10 or 13 digits.')
        return cleaned_isbn

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        subtitle = cleaned_data.get('subtitle')
        if title and subtitle and title.lower() == subtitle.lower():
            raise forms.ValidationError('Subtitle cannot be identical to the title.')
        return cleaned_data
```

### ModelForms

ModelForms automatically generate forms from Django models, avoiding duplicated field definitions.

```python
# books/forms.py
from django import forms
from .models import Book

class BookModelForm(forms.ModelForm):
    """Form for creating and updating Book instances."""

    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'author', 'publisher',
            'publication_date', 'genre', 'pages', 'summary',
            'cover_image', 'language', 'is_available', 'rating'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {'title': 'Book Title', 'publication_date': 'Date Published'}
        help_texts = {'rating': 'Rate the book from 1 to 5.'}
```

**Customizing a ModelForm** — extra fields, per-user field behavior, and a custom `save()`:

```python
class BookModelForm(forms.ModelForm):
    """Enhanced Book form with custom fields and validation."""
    confirm_terms = forms.BooleanField(
        required=True, label="I confirm that I have the rights to add this book"
    )

    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_staff:
            self.fields['is_available'].widget = forms.HiddenInput()
            self.fields['is_available'].initial = True

        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = 'form-control'

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        cleaned = isbn.replace('-', '').replace(' ', '')
        if len(cleaned) not in [10, 13]:
            raise forms.ValidationError('ISBN must be 10 or 13 digits.')
        return cleaned

    def save(self, commit=True):
        """Custom save behavior."""
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user

        if commit:
            instance.save()
            self.save_m2m()
        return instance
```

**ModelChoiceField for relationships:**

```python
class BookModelForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all().order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False, empty_label="No Publisher"
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'genre', 'pages', 'summary']
```

### Form Validation Layers

- Field-level validation: clean_<fieldname>() methods validate individual fields.
- Form-level validation: `clean()` validates relationships between fields.
- Model-level validation: constraints enforced when using a ModelForm.

```python
def clean_isbn(self):
    """Validate uniqueness, including on update."""
    isbn = self.cleaned_data.get('isbn')
    cleaned = ''.join(c for c in isbn if c.isdigit())
    if len(cleaned) not in [10, 13]:
        raise forms.ValidationError('ISBN must be 10 or 13 digits.')

    queryset = Book.objects.filter(isbn=cleaned)
    if self.instance.pk:
        queryset = queryset.exclude(pk=self.instance.pk)
    if queryset.exists():
        raise forms.ValidationError('A book with this ISBN already exists.')
    return cleaned
```

### Rendering Forms in Templates

```html
<!-- Automatic rendering -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

**Custom rendering with per-field control:**

```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {% for field in form %}
        <div class="mb-3 {% if field.errors %}has-error{% endif %}">
            <label for="{{ field.id_for_label }}" class="form-label">
                {{ field.label }}
                {% if field.field.required %}<span class="text-danger">*</span>{% endif %}
            </label>
            {{ field }}
            {% if field.help_text %}<small class="form-text text-muted">{{ field.help_text }}</small>{% endif %}
            {% for error in field.errors %}
                <div class="invalid-feedback d-block">{{ error }}</div>
            {% endfor %}
        </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary">Save</button>
</form>
```

**A custom filter for adding CSS classes to fields** (a common, idiomatic pattern):

```python
# books/templatetags/form_filters.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field's widget."""
    return field.as_widget(attrs={'class': css_class})
```

```html
{% load form_filters %}
{{ form.title|add_class:"form-control" }}
```

### Processing Forms in Views

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BookModelForm

def book_create(request):
    """Create a new book using a ModelForm."""
    if request.method == 'POST':
        form = BookModelForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" created successfully!')
            return redirect('book-detail', pk=book.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookModelForm(user=request.user)

    return render(request, 'books/book_form.html', {'form': form, 'title': 'Create Book'})
```

**Handling multiple forms on one page:**

```python
def book_create_with_author(request):
    """Create a book and optionally a new author."""
    if request.method == 'POST':
        book_form = BookModelForm(request.POST, request.FILES, user=request.user)
        author_form = AuthorForm(request.POST)

        if book_form.is_valid() and author_form.is_valid():
            if author_form.cleaned_data.get('create_new_author'):
                author = author_form.save()
                book = book_form.save(commit=False)
                book.author = author
                book.save()
                book_form.save_m2m()
            else:
                book = book_form.save()
            return redirect('book-detail', pk=book.pk)
    else:
        book_form = BookModelForm(user=request.user)
        author_form = AuthorForm()

    return render(request, 'books/book_with_author.html', {
        'book_form': book_form, 'author_form': author_form,
    })
```

**Processing a search form bound to GET data:**

```python
def book_search(request):
    """Search books using a search form."""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        genre = form.cleaned_data.get('genre')
        min_rating = form.cleaned_data.get('min_rating')

        if query:
            books = books.filter(
                Q(title__icontains=query) | Q(author__last_name__icontains=query)
            )
        if genre:
            books = books.filter(genre=genre)
        if min_rating:
            books = books.filter(rating__gte=min_rating)

    return render(request, 'books/search_results.html', {'form': form, 'books':
        books})
```

### Advanced Form Patterns

**Inline Formsets** — handling multiple related forms on one page:

```python
from django.forms import inlineformset_factory

BookCopyFormSet = inlineformset_factory(
    Book, BookCopy, fields=['copy_number', 'condition', 'location'],
    extra=3, max_num=5, can_delete=True,
)

def book_copy_management(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        formset = BookCopyFormSet(request.POST, instance=book)
        if formset.is_valid():
            formset.save()
            return redirect('book-detail', pk=book.pk)
    else:
        formset = BookCopyFormSet(instance=book)

    return render(request, 'books/copy_management.html', {'book': book, 'formset':
        formset})
```

**AJAX validation** for immediate feedback (e.g. checking ISBN uniqueness as the user types):

```python
from django.http import JsonResponse

def validate_isbn_ajax(request):
    """Validate ISBN via AJAX."""
    isbn = request.GET.get('isbn', '')
    cleaned = ''.join(c for c in isbn if c.isdigit())

    if len(cleaned) not in [10, 13]:
        return JsonResponse({'valid': False, 'message': 'ISBN must be 10 or 13 digits.'})

    exists = Book.objects.filter(isbn=cleaned).exclude(pk=request.GET.get('book_id',
        0)).exists()
    if exists:
        return JsonResponse({'valid': False, 'message': 'A book with this ISBN already exists.'})

    return JsonResponse({'valid': True, 'message': 'ISBN is valid.'})
```

### Security Considerations

```html
<!-- Always include CSRF token in POST forms -->
<form method="post">
    {% csrf_token %}
</form>
```

**Secure file upload validation:**

```python
import os

class SecureFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        """Validate uploaded file size, type, and extension."""
        file = self.cleaned_data.get('file')

        if file.size > 5 * 1024 * 1024: # 5MB
            raise forms.ValidationError('File size must be under 5MB.')

        if not file.content_type.startswith('image/'):
            raise forms.ValidationError('Only image files are allowed.')

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
            raise forms.ValidationError('Only JPG, PNG, and GIF images are allowed.')

        return file
```

### Testing Forms

```python
# tests/test_forms.py
from django.test import TestCase
from .forms import BookModelForm
from .models import Book, Author

class BookFormTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name='Test', last_name='Author')

    def test_form_valid_data(self):
        form = BookModelForm(data={
            'title': 'Test Book', 'author': self.author.id, 'isbn': '9781234567890',
            'publication_date': '2023-01-01', 'genre': 'F', 'pages': 200,
            'summary': 'Test summary',
        })
        self.assertTrue(form.is_valid())

    def test_form_duplicate_isbn(self):
        Book.objects.create(title='Existing Book', author=self.author,
            isbn='9781234567890', ...)
        form = BookModelForm(data={'isbn': '9781234567890', ...}) # Duplicate
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)
```

### Summary

- Basic Forms: fields, widgets, and validation.
- ModelForms: automatically generated forms tied to your models.
- Field-level, form-level, and model-level validation.
- Rendering forms manually, automatically, or with custom filters.
- Processing forms in views: single, multiple, and search forms.
- Advanced patterns: inline formsets and AJAX validation.
- Security: CSRF protection and secure file upload handling.
- Testing strategies for forms.

## 3.9 Chapter Summary and What's Next

We've reached the end of Chapter 3. We've moved from developers who could only handle simple views to ones who can build sophisticated, user-friendly applications with complex form handling and template logic.

### Chapter Recap

- 3.1 — The role of views, the request-response cycle, and FBVs vs. CBVs.
- 3.2 — HTTP method handling, GET/POST parameters, forms, AJAX, and advanced FBV patterns.
- 3.3 — The view hierarchy, TemplateView, RedirectView, and mixins.
- 3.4 — ListView and DetailView: customization, filtering, search, and pagination.
- 3.5 — CreateView, UpdateView, DeleteView, and FormView.
- 3.6 — Template variables, filters, tags, inheritance, and includes.
- 3.7 — Custom template tags and filters, context processors, and caching.
- 3.8 — Django's form system: basic forms, ModelForms, validation, and processing.

### Key Takeaways

- Views connect data to presentation — they handle the logic of your application.
- Class-Based Views offer powerful abstractions; use them for common patterns, FBVs for simple cases.
- Generic views save time by handling most common use cases with minimal code.
- Templates keep presentation clean — use inheritance and includes to avoid duplication.
- Custom tags and filters extend templates while keeping complex logic out of them.
- Forms handle user input securely — always validate and sanitize user data.
- Context processors provide global data for site-wide information.
- Performance matters — use caching, select_related, and prefetch_related.

### Looking Ahead: Chapter 4 — Authentication and Authorization

Now that you've mastered views, templates, and forms, it's time to secure your application. In Chapter 4, we'll explore:

- User Authentication: login, logout, and user registration.
- Permissions: restricting access to views and data.
- Groups: managing user permissions efficiently.
- Custom Users: extending the User model for custom fields.
- Password Management: reset, change, and validation.
- Session Management: understanding how Django tracks users.
- Security Best Practices: protecting your application from common threats.

### Practice Projects

- A Complete Book Management System: list, detail, create, update, delete views, search/filter/pagination, ModelForms, and custom template tags.
- A User-Generated Content Platform: registration, login, profile management, content creation/moderation, comments and reviews.

- An E-commerce Product Catalog: product listing with filtering/sorting, detail pages with related products, shopping cart, checkout forms.

### Final Words

You've completed one of the most extensive chapters in your Django journey. You now understand how to build the user-facing portion of your application — the views that handle logic, the templates that present data, and the forms that collect user input.

This knowledge, combined with your understanding of models from Chapter 2, gives you the complete picture of Django's MTV architecture. You can now build full-featured, data-driven web applications that handle user input securely and present data beautifully.

Remember: the best way to learn is to build. Start building your own projects, experiment with different patterns, and don't be afraid to make mistakes. Every mistake is a learning opportunity.

In the next chapter, we'll explore how to secure your applications with Django's authentication and authorization system. See you there!
