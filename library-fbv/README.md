# Library App with Function-Based Views

The working result of **"Building the Library App with Function-Based Views"** (Steps 1-10), built on the Chapter 2
`Author` / `Publisher` / `Book` models.

## Run it

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser     # needed to log in and add/edit/delete books
python manage.py seed_demo           # optional: 30 demo books so list, search and pagination have data
python manage.py runserver
```

Open http://127.0.0.1:8000/ (it redirects to `/books/`). Admin is at `/admin/`.

## Where each step of the guide lives

| Step | What | File |
|---|---|---|
| 1 | App structure (`myproject/`, `library/`) | whole project |
| 2 | `TEMPLATES['DIRS']`, `MEDIA_URL`, `MEDIA_ROOT`, media served in development | `myproject/settings.py`, `myproject/urls.py` |
| 3 | Project-level base template | `templates/base.html` |
| 4 | `BookModelForm`, `BookSearchForm` | `library/forms.py` |
| 5a | `book_list`, `book_detail` | `library/views.py` |
| 5b | `book_create`, `book_update`, `book_delete` | `library/views.py` |
| 5c | `book_search_ajax`, `book_toggle_availability`, `_params_without_page` | `library/views.py` |
| 6 | App URLs, `app_name = 'library'` | `library/urls.py` |
| 7 | Include in project URLs | `myproject/urls.py` |
| 8 | Pagination, list, detail, form, delete templates | `library/templates/` |
| 9 | Run-and-test checklist | `library/tests.py` (53 tests) |
| 10 | Search/sort/filter, pagination, messages, `created_by` ownership, AJAX endpoints | built in |

Models and admin are the Chapter 2 versions (`library/models.py`, `library/admin.py`), plus `created_by`
from Step 10, so edit/delete ownership checks are active.

## Fixes made to the guide as written

These would have broken the app if the guide's code were typed in exactly as printed:

1. **No `login` URL.** `base.html` uses `{% url 'login' %}` and `@login_required` redirects to a login page, but the
   guide never defines one, so every page raised `NoReverseMatch`. Fixed: `accounts/` auth URLs in `myproject/urls.py`,
   `templates/registration/login.html`, and `LOGIN_URL` / `LOGIN_REDIRECT_URL` in settings. A Logout button was added
   to the nav bar (Django 5+ logout is POST-only).
2. **`isbn` missing from `BookModelForm`.** `isbn` is a required, unique model field. Without it every book created through the
   form is saved with an empty ISBN and the second one fails with an `IntegrityError` (HTTP 500). Fixed: `isbn` added to the form.
3. **Wrong alert colour for errors.** Django's `error` message tag becomes `alert-error`, which Bootstrap doesn't have.
   Fixed with `MESSAGE_TAGS` in settings (error becomes `alert-danger`).
4. **Template tags split across lines** (PDF line wrapping, e.g. `{{ book.title` / `}}`, `{% include ... %}`). Django
   template tags must be on one line, so these were rejoined.

Small refinements: stable sort order in `book_list` (`pk` as tie-breaker, so pagination never repeats or skips ties),
`form-select` / `form-check-input` classes for selects and the checkbox, `&amp;` in pagination links, and `/` redirects to `/books/`.

## Behaviour to know about

- The Edit and Delete buttons show for any logged-in user (as in the guide); the views then return **403** unless the user
  created the book or is staff. Books with no creator (e.g. added in the admin) can be edited only by staff.
- `book_toggle_availability` and `book_search_ajax` aren't wired to a template yet (the guide leaves that as an exercise).

## Tests

```bash
python manage.py test library
```
Covers routes, every template, list search / filter / sort / pagination, detail and similar books, create / update / delete
including permissions and cover upload, the AJAX endpoints, login / logout, and the admin.
