# Junior-L

Educational programming content and curriculum materials.

## Contents

### Chapter Documents

- [`Django_Chapter1_Foundations.md`](./Django_Chapter1_Foundations.md) — Chapter 1 of a Django course:
  - 1.1 Introduction to Django
  - 1.2 Setting Up Your Django Development Environment
  - 1.3 Understanding the Project Structure and the manage.py Command
  - 1.4 Hello, World! Building Your First View

- [`Django_Chapter2_Models_and_Databases.md`](./Django_Chapter2_Models_and_Databases.md) — Chapter 2 of a Django course:
  - 2.1 Introduction to Databases and Django's ORM
  - 2.2 Configuring Your Database
  - 2.3 Defining Models: The Blueprint of Your Data
  - 2.4 Migrations: Evolving Your Database Schema
  - 2.5 The Django Admin Interface
  - 2.6 The Database API: Querying and Manipulating Data
  - 2.7 Model Relationships: Connecting Your Data
  - 2.8 Advanced Model Features
  - 2.9 Chapter Summary and What's Next

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
