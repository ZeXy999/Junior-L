# Junior-L

Educational programming content and curriculum materials.

## Contents

### Chapter Documents

- [`Django_Chapter1_Foundations.md`](./Django_Chapter1_Foundations.md) — Chapter 1 of a Django course:
  - 1.1 Introduction to Django
  - 1.2 Setting Up Your Django Development Environment
  - 1.3 Understanding the Project Structure and the manage.py Command
  - 1.4 Hello, World! Building Your First View

- [`Django_Chapter2_Models_and_Databases.md`](./Django_Chapter2_Models_and_Databases.md) — Chapter 2 of a Django course (sections 2.2–2.5):
  - 2.2 Configuring Your Database
  - 2.3 Defining Models: The Blueprint of Your Data
  - 2.4 Migrations: Evolving Your Database Schema
  - 2.5 The Django Admin Interface

- [`Django_Chapter3_Views_and_Templates.md`](./Django_Chapter3_Views_and_Templates.md) — Chapter 3 of a Django course:
  - 3.1 Introduction to Views
  - 3.2 Function-Based Views
  - 3.3 Class-Based Views
  - 3.4 Generic Display Views
  - 3.5 Generic Edit Views
  - 3.6 Template Fundamentals
  - 3.7 Advanced Template Features
  - 3.8 Forms in Django
  - 3.9 Chapter Summary and What's Next

### Library App (function-based views) — [`library-fbv/`](./library-fbv)

A complete Django library website: browse, search, filter, sort and paginate books, view details with similar titles,
and add / edit / delete books (with cover uploads, login and per-user permissions) through function-based views, Bootstrap templates,
the Django admin and 53 automated tests. Run it with `pip install -r requirements.txt`, `python manage.py migrate`,
`python manage.py seed_demo` and `python manage.py runserver` from inside `library-fbv/` (full instructions in [`library-fbv/README.md`](./library-fbv/README.md)).

### Working Code — [`exercises/django-textbook/`](./exercises/django-textbook)

A real Django project implementing what each chapter covers, tested end-to-end before being pushed.

**Chapter 1 — `hello_world` app** (practical exercises):
- **Exercise 1**: `/hello/<name>/` — personalized greeting via URL parameter
- **Exercise 2**: `/hello/about/` — name, bio, and top-5 favorites list
- **Exercise 3**: `/hello/numbers/` — loops a number list, flags even/odd, sums them
- **Exercise 4**: all pages extend a shared `base.html` (header, nav, footer)

**Chapter 2 — `library` app** (models, admin, ORM, relationships):
- `models.py` — `Author`, `Publisher`, `Genre`, `Book`, `BookAuthor` (through model), `BookCopy`, `Review`, covering `ForeignKey`, `ManyToManyField`, and validators
- `admin.py` — customized `ModelAdmin` classes with `list_display`, `list_filter`, `search_fields`, inlines, and custom actions
- `migrations/0001_initial.py` — generated and applied against a real SQLite database
- `test_library.py` — a script exercising CRUD, field lookups, `Q` objects, relationships, aggregation (`Count`/`Avg`/`Sum`), and `select_related()`/`prefetch_related()` — all verified to run and pass
