# Junior's Library

A complete library-management website built with Django by **Junior**.

Browse a catalog of books with generated cover art, read and write reviews, see star ratings and rating breakdowns, borrow and return copies, and manage everything through the Django admin.

## Features

- **Catalog** with search (title, author, ISBN), genre filter, "available now" filter, six sort orders and pagination
- **Book pages**: cover, summary, authors, publisher, ISBN, live copy availability, rating breakdown, related books
- **Ratings and reviews**: 1-5 stars, one review per reader (editable), average rating shown across the site
- **Borrowing**: 14-day loans, up to 5 at a time, per-copy tracking, overdue flags, return button
- **My Library**: current loans with days left or overdue, loan history, your reviews
- **Accounts**: sign up, log in, log out
- **Authors** pages with lifespan and bibliography
- **Admin**: books with inline copies, loans (with a "mark returned" action), reviews, authors, genres, publishers
- **Cover art** generated on the fly with Pillow, so no downloads or API keys are needed
- **Seed command** that fills the library with 31 classic novels plus randomly generated books, copies, readers, reviews and loans
- 10 automated tests

## Quick start

```bash
cd library-project
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_library     # classics + 12 random books, covers, reviews, loans
python manage.py runserver
```

Open http://127.0.0.1:8000/

The seed command prints the admin login (`junior`) and a generated password. To choose your own:

```bash
LIBRARY_ADMIN_PASSWORD=your-password python manage.py seed_library      # Windows PowerShell: $env:LIBRARY_ADMIN_PASSWORD="..."
```

### Seed options

| Option | What it does |
|---|---|
| `--extra 30` | Generate 30 random books on top of the classics (default 12) |
| `--reset` | Delete existing catalog data and demo readers first |
| `--seed 42` | Make the random data reproducible |
| `--no-covers` | Skip cover image generation |

The demo readers (`thandi`, `sipho`, ...) have no passwords. Use **Sign up** to create your own account and borrow or review books. Book metadata (ISBNs, publishers, copy counts, reviews) is demo data.

## Project layout

```
library-project/
├── manage.py
├── config/                 # settings, root URLs, wsgi
└── catalog/                # the library app
    ├── models.py           # Author, Publisher, Genre, Book, BookCopy, Loan, Review
    ├── views.py            # class-based list/detail views + borrow/return/review actions
    ├── forms.py, urls.py, admin.py, covers.py, tests.py
    ├── templatetags/       # stars filter, query-string helper
    ├── management/commands/seed_library.py
    └── templates/ + static/
```

## Tests

```bash
python manage.py test catalog
```

## Configuration

Environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1` by default; set `0` in production), `DJANGO_ALLOWED_HOSTS`.
