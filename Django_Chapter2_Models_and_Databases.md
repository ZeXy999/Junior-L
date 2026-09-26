# Chapter 2: Models and Databases

*Designing schemas, evolving them with migrations, managing data through the built-in admin, querying with the ORM, and modeling relationships.*

## Chapter Contents

- 2.1 Introduction to Databases and Django's ORM
- 2.2 Configuring Your Database
- 2.3 Defining Models: The Blueprint of Your Data
- 2.4 Migrations: Evolving Your Database Schema
- 2.5 The Django Admin Interface: A Built-In Data Management Tool
- 2.6 The Database API: Querying and Manipulating Data
- 2.7 Model Relationships: Connecting Your Data
- 2.8 Advanced Model Features
- 2.9 Chapter Summary and What's Next

---

## 2.1 Introduction to Databases and Django's ORM

Before we write our first model, it's essential to understand the landscape. What is a database? What is an ORM? And why has Django chosen this particular approach to data management?

### The Relational Database: A Brief Primer

At its most fundamental level, a relational database is a collection of structured data organized into tables. These tables consist of rows (records) and columns (fields). Each row represents a single instance of whatever entity you're storing, and each column represents a specific attribute of that entity.

| id | title | author | published_year | genre |
|----|-------|--------|-----------------|-------|
| 1 | The Great Gatsby | F. Scott Fitzgerald | 1925 | Fiction |
| 2 | To Kill a Mockingbird | Harper Lee | 1960 | Fiction |
| 3 | The Art of War | Sun Tzu | -500 | Strategy |

In SQL (Structured Query Language), the language used to interact with relational databases, we would retrieve all books from this table with a query like:

```sql
SELECT * FROM books;
```

And we would retrieve only fiction books with:

```sql
SELECT * FROM books WHERE genre = 'Fiction';
```

Relational databases are powerful, reliable, and the backbone of most web applications. However, writing raw SQL queries directly in your Python code presents several challenges:

- SQL is verbose and error-prone. String concatenation for dynamic queries is a security risk (SQL injection).
- SQL is database-specific. Switching from SQLite (development) to PostgreSQL (production) often requires rewriting queries.
- SQL doesn't integrate well with object-oriented programming. Converting rows into Python objects manually is repetitive and tedious.

This is where Django's ORM comes to the rescue.

### The Object-Relational Mapper (ORM)

An ORM is a programming technique that allows you to interact with your database using the object-oriented paradigm of your programming language. Instead of writing raw SQL, you work with Python classes (models) that represent your database tables. The ORM handles the translation between your Python code and the underlying SQL statements.

| Python Code | SQL Generated (Simplified) |
|---|---|
| `Book.objects.all()` | `SELECT * FROM books;` |
| `Book.objects.filter(genre='Fiction')` | `SELECT * FROM books WHERE genre = 'Fiction';` |
| `Book.objects.get(id=1)` | `SELECT * FROM books WHERE id = 1;` |
| `book.save()` | `INSERT INTO books (...) VALUES (...);` |

**Benefits of Using Django's ORM:**

- **Pythonic Syntax**: you write Python, not SQL — more readable and maintainable.
- **Database Agnosticism**: the ORM generates SQL appropriate to your engine; switching databases requires minimal code changes.
- **Security**: automatic escaping of user input protects against SQL injection.
- **Productivity**: complex joins and aggregations require far less code.
- **Portability**: database-agnostic models simplify migrating to different systems.

**Trade-offs of Using an ORM:**

- **Performance**: for extremely complex queries, raw SQL can be more efficient. Django provides escape hatches when needed.
- **Learning Curve**: understanding the ORM's behavior requires learning its API and conventions.
- **Abstraction Leak**: sometimes you need to see the generated SQL to optimize your queries.

Django strikes an excellent balance. For 95% of use cases, the ORM is the perfect tool. For the remaining 5%, Django provides escape hatches to write raw SQL or optimize queries manually.

### How Django Models Relate to Database Tables

A Django model is a Python class that inherits from `django.db.models.Model`. Each attribute of the class represents a database field. Django automatically creates a corresponding database table for each model, with columns that match the fields you define.

```python
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_year = models.IntegerField()

# Roughly maps to:
# CREATE TABLE books (
#     id INTEGER PRIMARY KEY,
#     title VARCHAR(100),
#     author VARCHAR(100),
#     published_year INTEGER
# );
```

Django automatically adds an `id` field as the primary key unless you specify a custom one. It also manages table and column naming conventions, though you can customize these.

### A High-Level Overview of Django's Database Layer

- **Models**: Python classes that define your data structure.
- **Migrations**: the mechanism for evolving your database schema over time.
- **QuerySet API**: the powerful interface for querying and manipulating data.
- **Database Backend**: translates ORM operations into SQL specific to your database.
- **Connection Management**: handles database connections and connection pooling.

### Prerequisites for This Chapter

- A working Django development environment (as set up in Chapter 1).
- A Django project with a configured database (we'll use SQLite by default).
- A new app where we'll define our models.

```bash
python manage.py startapp library
```

(We'll use this `library` app for our examples throughout this chapter.) Don't forget to add `'library'` to `INSTALLED_APPS` in your `settings.py`!

### Summary

- The role of relational databases in web applications.
- The challenges of working with raw SQL directly.
- What an ORM is and how Django's ORM addresses these challenges.
- The benefits (productivity, security, database agnosticism) and trade-offs (performance, learning curve) of using an ORM.
- How Django models map to database tables.

---

## 2.2 Configuring Your Database

Now that we understand the theory behind Django's ORM, it's time to prepare our environment for database work. In this section, we will explore Django's database configuration, understand the default SQLite setup, and learn how to configure other production-ready databases like PostgreSQL and MySQL.

### The Default Database: SQLite

When you create a new Django project, it comes pre-configured with SQLite as the default database engine:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

- `'default'`: the name of the database connection — sufficient for most projects.
- `'ENGINE'`: which database backend to use (sqlite3, postgresql, mysql, oracle).
- `'NAME'`: for SQLite, the path to the database file — a single, self-contained file.

**Advantages of SQLite for Development**: zero configuration, portability (a single file), lightweight, no server required.

**Limitations of SQLite**: not suitable for high traffic or heavy concurrent writes, limited feature set, generally not recommended for production.

### Configuring PostgreSQL

PostgreSQL is widely considered the best database for Django applications — robust, feature-rich, and highly performant.

**Step 1 — Install PostgreSQL**: Windows (installer from postgresql.org), macOS (`brew install postgresql`), Linux (`sudo apt install postgresql postgresql-contrib`).

**Step 2 — Install the Python adapter:**

```bash
pip install psycopg2-binary
```

**Step 3 — Create a database and user:**

```sql
CREATE DATABASE mydatabase;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
```

**Step 4 — Update settings.py:**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',  # Default PostgreSQL port
    }
}
```

**Pro Tip**: never hard-code database credentials in `settings.py`. Use environment variables instead:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydatabase'),
        'USER': os.environ.get('DB_USER', 'myuser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'mypassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

### Configuring MySQL

MySQL is another popular choice, particularly for developers transitioning from PHP. Django supports MySQL, but PostgreSQL is generally preferred for new Django projects.

**Step 1 — Install MySQL**: Windows (mysql.com installer), macOS (`brew install mysql`), Linux (`sudo apt install mysql-server`).

**Step 2 — Install the Python adapter:**

```bash
pip install mysqlclient
# On Ubuntu you may also need:
# sudo apt install libmysqlclient-dev
```

**Step 3 — Create a database and user:**

```sql
CREATE DATABASE mydatabase CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'myuser'@'localhost';
FLUSH PRIVILEGES;
```

**Step 4 — Update settings.py:**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

**Note**: the `OPTIONS` setting with `init_command` ensures MySQL uses strict mode, which is recommended for Django.

### Additional Database Configuration Options

**Connection Pooling** — `CONN_MAX_AGE` controls how long connections persist between requests:

```python
'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
```

**Connection Health Checks** (Django 4.1+):

```python
'CONN_HEALTH_CHECKS': True,
```

**ATOMIC_REQUESTS** — wraps each HTTP request in a database transaction, rolling back on error:

```python
'ATOMIC_REQUESTS': True,
```

This is convenient for data consistency but can impact performance — recommended for production, used mindfully.

### Testing Your Database Configuration

**Step 1 — Check connectivity:**

```bash
python manage.py check
```

**Step 2 — Run initial migrations** (creates tables for admin, auth, contenttypes, etc.):

```bash
python manage.py migrate
```

**Step 3 — Verify the tables:**

```bash
# SQLite
sqlite3 db.sqlite3
.tables

# PostgreSQL
psql -d mydatabase -U myuser
\dt

# MySQL
mysql -u myuser -p mydatabase
SHOW TABLES;
```

You should see tables like `auth_user`, `auth_group`, `django_session`, `django_migrations`, and others.

### Setting Up a Separate Test Database

When you run tests, Django automatically creates a separate test database, named `test_` plus your database name by default:

```python
'TEST': {
    'NAME': 'test_mydatabase',  # Override the test database name
},
```

### Switching Between Development and Production

A common pattern is to use environment variables:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}
```

Another common pattern is separate settings files per environment (`base.py`, `development.py`, `testing.py`, `production.py`), each overriding environment-specific settings.

### Troubleshooting Common Database Configuration Issues

| Issue | Likely Cause | Solution |
|---|---|---|
| `OperationalError: unable to open database file` | SQLite file path issue or permissions | Ensure the `db.sqlite3` path is correct and the directory is writable. |
| `OperationalError: could not connect to server` | PostgreSQL server not running | Start the service: `sudo systemctl start postgresql` (Linux). |
| `OperationalError: Access denied for user` | MySQL authentication failure | Verify username, password, and host access. |
| `ModuleNotFoundError: No module named 'psycopg2'` | Adapter not installed | `pip install psycopg2-binary` |
| `OperationalError: no such table` | Schema not created | Run `python manage.py migrate` |

### Summary

- SQLite: the default, file-based database perfect for development.
- PostgreSQL: the recommended production database with rich features.
- MySQL: another solid, widely supported option.
- Environment Variables: best practice for managing sensitive credentials.
- Testing your configuration and troubleshooting common issues.

---

## 2.3 Defining Models: The Blueprint of Your Data

With our database configured, we arrive at the most fundamental task in building a data-driven application: defining our models. Models are the single source of truth about your database schema and the foundation upon which your entire application is built.

### Understanding Models

A Django model is a Python class that inherits from `django.db.models.Model`. Each attribute represents a database field, and the class represents a database table. Django automatically adds an `id` field as the primary key — an auto-incrementing integer — unless you specify a custom one.

### Creating Our First Model

Let's build a model for a library application, starting with a `Book` model.

```python
from django.db import models

class Book(models.Model):
    """
    A model representing a book in the library.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    genre = models.CharField(max_length=50)
    pages = models.IntegerField()
    summary = models.TextField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Human-readable representation of the book."""
        return self.title
```

### Field Types: Django's Data Types

| Field Type | Description | Example |
|---|---|---|
| `CharField` | Short/medium text (needs max_length) | `CharField(max_length=200)` |
| `TextField` | Long, unlimited text | `TextField()` |
| `IntegerField` | Integer numbers | `IntegerField()` |
| `FloatField` | Floating-point numbers | `FloatField()` |
| `DecimalField` | Fixed-precision decimals | `DecimalField(max_digits=10, decimal_places=2)` |
| `DateField` | Date (year, month, day) | `DateField()` |
| `DateTimeField` | Date and time | `DateTimeField(auto_now_add=True)` |
| `BooleanField` | True/False | `BooleanField(default=True)` |
| `EmailField` | Validates emails | `EmailField()` |
| `URLField` | Validates URLs | `URLField()` |
| `UUIDField` | Stores UUIDs | `UUIDField()` |
| `FileField` | File uploads | `FileField(upload_to='uploads/')` |
| `ImageField` | Image uploads | `ImageField(upload_to='images/')` |
| `JSONField` | JSON data (PostgreSQL, 3.1+) | `JSONField()` |

### Field Options: Customizing Your Fields

| Option | Description | Example |
|---|---|---|
| `max_length` | Max length of a string field | `max_length=200` |
| `null` | Allow NULL in the database | `null=True` |
| `blank` | Allow empty values in forms | `blank=True` |
| `default` | Default value | `default=True` |
| `unique` | Values must be unique | `unique=True` |
| `choices` | Limits to predefined values | `choices=[('F','Fiction')]` |
| `help_text` | Extra text in the admin | `help_text="The ISBN"` |
| `verbose_name` | Human-readable field name | `verbose_name="Title"` |
| `db_index` | Creates a database index | `db_index=True` |
| `auto_now_add` | Set to now on creation | `auto_now_add=True` |
| `auto_now` | Set to now on every save | `auto_now=True` |

**Understanding `null` vs `blank`**: `null` is database-level — if `True`, the column can store NULL. `blank` is validation-level — if `True`, the field is not required in forms.

- `CharField` and `TextField`: `blank=True` is common; `null=True` is rarely used.
- `DateField` and `DateTimeField`: use `null=True` if you need to allow empty values.
- `BooleanField`: use `default` instead of `null`.

### Adding the `__str__()` Method

The `__str__()` method returns a human-readable string representation of the object, used in the admin, the shell, and elsewhere.

```python
def __str__(self):
    return f"{self.title} by {self.author}"
```

**Best Practice**: always define `__str__()` for your models — it makes debugging and administration vastly easier.

### Adding a Meta Class

The `Meta` class provides metadata about your model — information not directly related to its fields.

```python
class Book(models.Model):
    # ... fields ...

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        db_table = 'library_books'
```

| Option | Description | Example |
|---|---|---|
| `ordering` | Default ordering for the model | `ordering = ['-created_at']` |
| `verbose_name` | Singular name for the model | `verbose_name = "Book"` |
| `verbose_name_plural` | Plural name | `verbose_name_plural = "Books"` |
| `db_table` | Custom database table name | `db_table = 'library_books'` |
| `unique_together` | Unique combination of fields | `unique_together = [['title','author']]` |
| `indexes` | Explicit index definitions | `indexes = [models.Index(...)]` |
| `constraints` | Database constraints | `constraints = [models.CheckConstraint(...)]` |

### Using `choices` for Limited Values

The `choices` option is useful when a field should only accept values from a predefined list — it provides both validation and a friendly admin UI.

```python
class Book(models.Model):
    GENRE_CHOICES = [
        ('F', 'Fiction'),
        ('NF', 'Non-Fiction'),
        ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'),
        ('MYS', 'Mystery'),
        ('THR', 'Thriller'),
        ('ROM', 'Romance'),
        ('HIS', 'Historical'),
        ('BIO', 'Biography'),
    ]
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default='F')
```

Django provides helper methods to work with choices:

```python
book = Book.objects.get(id=1)
print(book.get_genre_display())  # e.g., "Fiction"
```

### Creating a More Complex Model

Let's expand our `Book` model with related models — `Author` and `Publisher` — bringing several concepts together (relationships are covered in depth in Section 2.7):

```python
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    established = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    GENRE_CHOICES = [
        ('F', 'Fiction'), ('NF', 'Non-Fiction'), ('SF', 'Science Fiction'),
        ('FAN', 'Fantasy'), ('MYS', 'Mystery'), ('THR', 'Thriller'),
        ('ROM', 'Romance'), ('HIS', 'Historical'), ('BIO', 'Biography'),
        ('SCI', 'Science'), ('TEC', 'Technology'),
    ]

    title = models.CharField(max_length=200, help_text="The book's full title")
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True,
                             help_text="The book's unique 13-digit ISBN")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='books')
    publication_date = models.DateField()
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default='F')
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    summary = models.TextField(help_text="Brief description of the book")
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    is_available = models.BooleanField(default=True)
    borrowed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def full_title(self):
        if self.subtitle:
            return f"{self.title}: {self.subtitle}"
        return self.title

    def is_recent(self):
        return (timezone.now().date() - self.publication_date).days < 1825

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['genre']),
        ]
```

### Validation in Models

**1. Built-in Validators:**

```python
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator

class Book(models.Model):
    pages = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10000)])
    email = models.EmailField(validators=[EmailValidator(message="Enter a valid email.")])
```

**2. Model-Level Validation with `clean()`:**

```python
class Book(models.Model):
    # ... fields ...

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.publication_date and self.publication_date > timezone.now().date():
            raise ValidationError({
                'publication_date': "Publication date cannot be in the future."
            })
        if self.isbn and len(self.isbn) != 13:
            raise ValidationError({'isbn': "ISBN must be exactly 13 characters."})
```

**3. Database Constraints in Meta** (Django 2.2+):

```python
class Book(models.Model):
    # ... fields ...

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(pages__gte=1), name='pages_positive'),
            models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author'),
        ]
```

### Making Migrations After Defining Models

```bash
python manage.py makemigrations library
```

```
Migrations for 'library':
  library/migrations/0001_initial.py
    - Create model Author
    - Create model Publisher
    - Create model Book
```

You can examine the migration to see the raw SQL Django will execute:

```bash
python manage.py sqlmigrate library 0001
```

Then apply the migrations:

```bash
python manage.py migrate
```

### Using the Django Shell to Test Your Models

```bash
python manage.py shell
```

```python
from library.models import Author, Publisher, Book
from datetime import date

author = Author(
    first_name="George", last_name="Orwell",
    birth_date=date(1903, 6, 25), death_date=date(1950, 1, 21),
    biography="British novelist and essayist, journalist and critic."
)
author.save()

publisher = Publisher(name="Secker & Warburg", city="London",
                       country="UK", established=date(1936, 1, 1))
publisher.save()

book = Book(
    title="Nineteen Eighty-Four", isbn="9780451524935",
    author=author, publisher=publisher,
    publication_date=date(1949, 6, 8), genre="SF", pages=328,
    summary="A dystopian social science fiction novel and cautionary tale.",
    language="English"
)
book.save()

all_books = Book.objects.all()
print(f"Total books: {all_books.count()}")

recent_books = Book.objects.filter(publication_date__year__gte=2020)
print(f"Recent books: {recent_books.count()}")

exit()
```

### Best Practices for Defining Models

- Start simple — begin with the minimal fields you need; add more later.
- Use appropriate field types (e.g., `EmailField` instead of `CharField` for validation).
- Always define `__str__()` to make models human-readable.
- Use `verbose_name` and `verbose_name_plural` for a friendlier admin.
- Set default `ordering` in `Meta` for consistent query results.
- Add indexes to frequently queried fields.
- Use `auto_now_add` and `auto_now` to automate timestamps.
- Document models with docstrings and `help_text`.
- Keep migrations small and incremental.
- Think about relationships early — changing them later can be complex.

### Common Mistakes to Avoid

| Mistake | Why It's Wrong | Solution |
|---|---|---|
| Forgetting `max_length` on CharField | Django requires it | Always specify `max_length` |
| Using `null=True` unnecessarily | Creates unneeded nullable columns | Use only when necessary |
| Forgetting to run `migrate` | Schema changes aren't applied | Run `makemigrations` then `migrate` |
| Not defining `__str__()` | Objects display unhelpfully | Always add `__str__()` |
| Using `TextField` for short strings | Wastes database space | Use `CharField` for short strings |
| Hard-coding choices inline | Harder to maintain | Define choices as a class constant |

### Summary

- What models are and how they map to database tables.
- Common field types and field options.
- The `__str__()` method and the `Meta` class.
- Using `choices` to limit values to predefined options.
- Validation via validators, `clean()`, and database constraints.
- Creating and applying migrations, and testing models in the shell.
- Best practices for building clean, maintainable models.

---

## 2.4 Migrations: Evolving Your Database Schema

As your application evolves, you'll need to add new fields, modify existing ones, and sometimes restructure your data models entirely. Django's migration system provides a version-controlled, automated way to evolve your database schema alongside your code, preserving your data throughout the process.

### What Are Migrations?

Migrations are Django's way of propagating changes you make to your models into your database schema. They are Python files containing operations that describe what changes need to be made.

- **Migration File**: a Python file (generated by `makemigrations`) describing schema changes.
- **Applied Migration**: a migration that has been executed against your database.
- **Migration History**: a record of applied migrations, stored in the `django_migrations` table.
- **Rollback**: the process of undoing a migration, reverting to a previous state.

### The Migration Workflow

```
1. Modify your models (add/change/delete fields or models)
        |
2. Run `python manage.py makemigrations`
        |
3. Review the generated migration file
        |
4. Run `python manage.py migrate`
        |
5. Your database schema is updated
```

### Step 1: Creating Migrations with makemigrations

```bash
python manage.py makemigrations
```

This examines all your apps, detects model changes, and creates migration files for any app with changes.

```bash
python manage.py makemigrations library                              # target a specific app
python manage.py makemigrations library --name add_publication_year   # a descriptive name
```

```
Migrations for 'library':
  library/migrations/0002_add_publication_year.py
    - Add field publication_year to book
```

### Step 2: Understanding Migration Files

```python
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publication_year',
            field=models.IntegerField(default=2023),
        ),
    ]
```

| Operation | Description |
|---|---|
| `AddField` | Adds a new field to a model |
| `RemoveField` | Removes a field from a model |
| `AlterField` | Changes a field's attributes |
| `RenameField` | Renames a field |
| `AddIndex` | Adds an index to a field |
| `CreateModel` | Creates a new model |
| `DeleteModel` | Deletes a model (destructive!) |
| `RenameModel` | Renames a model |

### Step 3: Reviewing Migrations

```bash
python manage.py sqlmigrate library 0002
```

```sql
BEGIN;
--
-- Add field publication_year to book
--
ALTER TABLE "library_book" ADD COLUMN "publication_year" integer DEFAULT 2023 NOT NULL;
ALTER TABLE "library_book" ALTER COLUMN "publication_year" DROP DEFAULT;
COMMIT;
```

```bash
python manage.py showmigrations
```

```
library
 [X] 0001_initial
 [ ] 0002_add_publication_year
```

`[X]` = applied, `[ ]` = not applied.

### Step 4: Applying Migrations with migrate

```bash
python manage.py migrate                  # applies all pending migrations
python manage.py migrate library          # for a specific app
python manage.py migrate library 0002     # up to and including migration 0002
```

**Fake Migrations** (use with caution!):

```bash
python manage.py migrate library --fake
```

This marks migrations as applied without running them — useful when your schema already matches, or to recover from a failed migration state. Warning: can leave your database inconsistent if used carelessly.

### Step 5: Rolling Back Migrations

```bash
python manage.py migrate library 0001    # roll back to migration 0001
python manage.py migrate library zero    # roll back ALL migrations for the app
```

### Data Migrations

Sometimes you need to move or transform data when changing your schema. Django provides `RunPython` for this.

Example: splitting `publication_date` into `publication_year` and `publication_month`.

```bash
python manage.py makemigrations library --empty --name populate_publication_parts
```

```python
from django.db import migrations

def populate_publication_parts(apps, schema_editor):
    """Populate the new year and month fields from the old date field."""
    Book = apps.get_model('library', 'Book')
    for book in Book.objects.all():
        book.publication_year = book.publication_date.year
        book.publication_month = book.publication_date.month
        book.save()

def reverse_populate(apps, schema_editor):
    """Reverse the data migration if needed."""
    Book = apps.get_model('library', 'Book')
    for book in Book.objects.all():
        book.publication_date = f"{book.publication_year}-{book.publication_month}-01"
        book.save()

class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_add_publication_fields'),
    ]

    operations = [
        migrations.RunPython(populate_publication_parts, reverse_populate),
    ]
```

- Use `apps.get_model()`: ensures you're using the model as it existed at migration time.
- Make them reversible: provide a reverse function to handle rollbacks gracefully.
- Be mindful of performance: batch operations for large datasets.

### Managing Dependencies

```python
class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_add_publication_year'),
        ('auth', '0011_update_proxy_permissions'),
    ]
```

Dependencies ensure migrations are applied in the correct order — common scenarios include app dependencies, foreign keys across apps, and third-party app migrations.

### Squashing Migrations

Over time your project may accumulate dozens of migration files, slowing down `migrate` and `makemigrations`. Squashing combines multiple migrations into one.

```bash
python manage.py squashmigrations library 0001 0010
```

Squash before a major release, when you have more than ~50 migrations, or when migrations slow your CI/CD. Important: only squash after migrations have been applied everywhere — squashing out of order can cause issues.

### Best Practices for Migration Management

- Commit migrations to version control — they're code.
- Run migrations in development first, thoroughly, before production.
- Back up your database before major changes, especially squashing.
- Make small, incremental changes — easier to roll back.
- Test rollbacks to ensure they work without data loss.
- Use descriptive names: `makemigrations library --name add_author_foreign_key`
- Review migration SQL before applying: `sqlmigrate`.
- Avoid data loss: prefer `null=True` over deleting fields, use defaults for new required fields.
- Preview actions with `migrate --plan`.
- Keep migration files clean and simple.

### Troubleshooting Common Migration Issues

| Issue | Likely Cause | Solution |
|---|---|---|
| `NodeNotFoundError` | Missing dependency | Check migration dependencies exist. |
| Conflicting migrations | Parallel migration branches | Resolve by choosing or merging manually. |
| `OperationalError: no such column` | Migration not applied | Run `python manage.py migrate`. |
| `IntegrityError` | Data conflict | Use data migrations to clean up first. |
| Migration failed halfway | Partial application | Roll back to zero, then retry. |
| `InconsistentMigrationHistory` | Manual DB changes | Use `--fake` carefully or reset history. |

### Advanced Migration Techniques

**Atomic vs. Non-Atomic Migrations**: by default migrations are atomic. For MySQL, some operations aren't atomic:

```python
class Migration(migrations.Migration):
    atomic = False  # Disable atomicity for this migration

    operations = [
        # ... operations that might fail partially
    ]
```

**Using RunSQL for database-specific operations:**

```python
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            sql="CREATE INDEX book_title_idx ON library_book (title);",
            reverse_sql="DROP INDEX book_title_idx;",
        ),
    ]
```

### A Complete Migration Example

**Scenario**: add a `rating` field to `Book`, and populate it for existing books.

**Step 1 — Modify the model:**

```python
class Book(models.Model):
    # ... existing fields ...
    rating = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
```

**Step 2 — Create the migration:**

```bash
python manage.py makemigrations library --name add_rating_field
```

**Step 3 — Create a data migration:**

```bash
python manage.py makemigrations library --empty --name populate_ratings
```

**Step 4 — Edit the data migration:**

```python
from django.db import migrations
import random

def set_initial_ratings(apps, schema_editor):
    Book = apps.get_model('library', 'Book')
    for book in Book.objects.all():
        book.rating = random.randint(1, 5)
        book.save()

class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_add_rating_field'),
    ]

    operations = [
        migrations.RunPython(set_initial_ratings),
    ]
```

**Step 5 — Apply, and Step 6 — verify:**

```bash
python manage.py migrate library
python manage.py shell
```

```python
>>> from library.models import Book
>>> for book in Book.objects.all():
...     print(f"{book.title}: {book.rating}★")
```

### Summary

- Migrations are version-controlled steps for evolving your database schema.
- The workflow: modify models -> makemigrations -> review -> migrate.
- Migration file structure, operations, and dependencies.
- Reviewing with `sqlmigrate` and `showmigrations`.
- Applying, rolling back, and faking migrations.
- Data migrations with `RunPython`, and squashing to keep history manageable.
- Best practices and common troubleshooting.

---

## 2.5 The Django Admin Interface: A Built-In Data Management Tool

One of Django's most celebrated "batteries-included" features is its automatically generated admin interface — a fully functional, production-ready administrative dashboard that lets you manage your application's data without writing a single line of administrative code.

### Why the Admin Interface Matters

- **Rapid Content Management**: acts as a complete CMS out of the box for content-heavy sites.
- **Development Productivity**: a convenient way to create, view, modify, and delete test data.
- **Client Empowerment**: hand it to non-technical staff for content management.
- **Debugging and Maintenance**: a clear window into your application's data.
- **Time Savings**: can save days or weeks of custom admin tool development.

### Activating the Admin Interface

The admin interface is already configured when you create a new project.

**Step 1** — Check `INSTALLED_APPS` (`django.contrib.admin` is already listed).

**Step 2** — Check the URL configuration (already mapped in the project's `urls.py`):

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
```

**Step 3** — Run migrations:

```bash
python manage.py migrate
```

**Step 4** — Create a superuser:

```bash
python manage.py createsuperuser
```

**Step 5** — Access the interface:

```bash
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

### The Default Admin Dashboard

The dashboard shows a sidebar of available apps and models, a log of recent actions, and built-in user/group management. Your custom models (`Book`, `Author`, `Publisher`) won't appear until you register them.

### Registering Models with the Admin Site

Create or edit `library/admin.py`:

```python
from django.contrib import admin
from .models import Author, Publisher, Book

admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Book)
```

Refresh the dashboard and you'll see your models under "Library" — you can view, edit, add, search, filter, and sort.

### Customizing Model Administration

**Step 1** — Create a `ModelAdmin` class:

```python
from django.contrib import admin
from .models import Book, Author, Publisher

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Custom admin configuration for the Book model."""
    pass
```

**Step 2** — Add customizations:

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_date', 'is_available', 'rating')
    list_filter = ('genre', 'is_available', 'publication_date', 'author')
    search_fields = ('title', 'subtitle', 'author__first_name', 'author__last_name', 'isbn')
    ordering = ('title',)
    date_hierarchy = 'publication_date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'isbn', 'author', 'publisher')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'genre', 'pages', 'language')
        }),
        ('Content', {
            'fields': ('summary', 'cover_image'),
            'classes': ('collapse',)
        }),
        ('Availability', {
            'fields': ('is_available', 'borrowed_count')
        }),
        ('Ratings', {
            'fields': ('rating',),
            'classes': ('wide',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_unavailable', 'mark_as_available']

    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} books were marked as available.')
    mark_as_available.short_description = "Mark selected books as available"

    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} books were marked as unavailable.')
    mark_as_unavailable.short_description = "Mark selected books as unavailable"
```

### Understanding ModelAdmin Options

| Option | Description | Example |
|---|---|---|
| `list_display` | Fields shown in the list view | `('title','author','genre')` |
| `list_display_links` | Fields that link to detail view | `('title',)` |
| `list_filter` | Filters in the sidebar | `('genre','is_available')` |
| `search_fields` | Fields searchable via the search box | `('title','author__last_name')` |
| `ordering` | Default ordering of the list | `('-publication_date','title')` |
| `date_hierarchy` | Date-based drill-down navigation | `'publication_date'` |
| `fieldsets` | Group fields in the edit form | see example above |
| `exclude` | Fields to hide in the edit form | `('created_at','updated_at')` |
| `readonly_fields` | Fields that cannot be edited | `('slug','created_at')` |
| `actions` | Custom actions on selected items | see example above |
| `list_editable` | Fields editable in the list view | `('is_available','rating')` |
| `list_per_page` | Number of items per page | `25` (default) |
| `save_on_top` | Show save buttons at the top | `True` |
| `prepopulated_fields` | Auto-populate from other fields | `{'slug': ('title',)}` |
| `inlines` | Inline editing of related models | see next section |

### Working with Inlines

Inlines let you edit related models on the same page as the parent — invaluable for one-to-many relationships.

```python
from django.contrib import admin
from .models import Author, Book

class BookInline(admin.TabularInline):  # or admin.StackedInline
    model = Book
    extra = 1
    fields = ('title', 'publication_date', 'genre', 'is_available')
    show_change_link = True

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date')
    search_fields = ('last_name', 'first_name')
    inlines = [BookInline]
```

`TabularInline` shows related objects in a compact table; `StackedInline` is more spacious and form-like — choose based on field count and readability.

### Customizing the Admin Interface Appearance

```python
# my_admin.py
from django.contrib.admin import AdminSite

class CustomAdminSite(AdminSite):
    site_header = "My Library Admin"
    site_title = "Library Management"
    index_title = "Welcome to the Library Administration"


class BookAdmin(admin.ModelAdmin):
    # ... other options ...
    class Media:
        css = {'all': ('css/admin_custom.css',)}
        js = ('js/admin_custom.js',)
```

### Advanced Admin Features

**1. Foreign Key Autocomplete** (fast for large datasets):

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ['author', 'publisher']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
```

**2. Raw ID Fields** (a popup selector instead of a dropdown):

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    raw_id_fields = ['author', 'publisher']
```

**3. Custom Admin Methods** (e.g., a cover thumbnail):

```python
from django.utils.html import format_html

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'cover_thumbnail', 'is_available')

    def cover_thumbnail(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" height="50px" />', obj.cover_image.url)
        return "No cover"
    cover_thumbnail.short_description = "Cover"
```

**4. Editable List View:**

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_available', 'rating')
    list_editable = ('is_available', 'rating')
```

**5. Custom Filter:**

```python
from django.contrib.admin import SimpleListFilter

class RecentBooksFilter(SimpleListFilter):
    title = 'Publication Date'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('recent', 'Published in last 5 years'),
            ('older', 'Published over 5 years ago'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        five_years_ago = timezone.now().date() - timedelta(days=1825)
        if self.value() == 'recent':
            return queryset.filter(publication_date__gte=five_years_ago)
        if self.value() == 'older':
            return queryset.filter(publication_date__lt=five_years_ago)
        return queryset

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_filter = (RecentBooksFilter, 'genre', 'is_available')
```

### Security Considerations for the Admin Interface

**1. Restrict access:**

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author__user=request.user)
```

**2. Custom permissions:**

```python
class Book(models.Model):
    # ... fields ...
    class Meta:
        permissions = [
            ("can_publish_book", "Can publish books"),
            ("can_unpublish_book", "Can unpublish books"),
        ]
```

- Use HTTPS in production to prevent credential interception.
- Change the default `/admin/` URL to something more obscure.
- Limit login attempts using Django's auth views or a third-party package.

### A Complete Admin Configuration Example

```python
from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import Author, Publisher, Book


class BookInline(admin.TabularInline):
    model = Book
    extra = 0
    fields = ('title', 'publication_date', 'genre', 'is_available')
    show_change_link = True


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'book_count', 'is_active')
    list_filter = ('birth_date',)
    search_fields = ('last_name', 'first_name', 'email')
    ordering = ('last_name', 'first_name')
    date_hierarchy = 'birth_date'
    inlines = [BookInline]

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Number of Books"

    def is_active(self, obj):
        return obj.death_date is None
    is_active.boolean = True
    is_active.short_description = "Active"


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'established', 'book_count')
    list_filter = ('country', 'established')
    search_fields = ('name', 'city', 'country')
    ordering = ('name',)

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Number of Books"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_date', 'is_available', 'rating', 'age')
    list_filter = ('genre', 'is_available', 'publication_date', 'author')
    search_fields = ('title', 'subtitle', 'isbn', 'author__first_name', 'author__last_name')
    ordering = ('-publication_date',)
    date_hierarchy = 'publication_date'
    list_editable = ('is_available', 'rating')
    list_per_page = 25
    save_on_top = True
    readonly_fields = ('created_at', 'updated_at', 'age')
    autocomplete_fields = ['author', 'publisher']
    actions = ['mark_as_available', 'mark_as_unavailable', 'increase_rating']

    def age(self, obj):
        years = (now().date() - obj.publication_date).days // 365
        return f"{years} years" if years >= 0 else "Not yet published"
    age.short_description = "Age"

    def mark_as_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} books marked as available.')
    mark_as_available.short_description = "Mark selected books as available"

    def mark_as_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} books marked as unavailable.')
    mark_as_unavailable.short_description = "Mark selected books as unavailable"

    def increase_rating(self, request, queryset):
        for book in queryset:
            if book.rating < 5:
                book.rating += 1
                book.save()
        self.message_user(request, f'Rating increased for {queryset.count()} books.')
    increase_rating.short_description = "Increase rating by 1"
```

### Using the Admin Interface

- **Adding data**: click "Add" next to any model, fill in the form, click "Save."
- **Editing data**: click any record, modify fields, click "Save."
- **Searching**: use the search box (supports partial matches and multiple terms).
- **Filtering**: use sidebar filters, combinable for complex queries.
- **Bulk operations**: select records, choose an action, apply it.
- **Viewing history**: click "History" on a record to see its change log.

### Summary

- Activating the admin, and creating a superuser.
- Registering models to make them visible in the admin.
- Customizing `ModelAdmin` with `list_display`, `list_filter`, `search_fields`, and `fieldsets`.
- Working with inlines to edit related models on one page.
- Custom actions for bulk operations.
- Security considerations for protecting the admin interface.
- A complete, comprehensive configuration example.

---

## 2.6 The Database API: Querying and Manipulating Data

Django's Database API is one of the most powerful and intuitive ORM interfaces available. It allows you to create, retrieve, update, and delete records using Python code that reads like natural language.

### Understanding the QuerySet

A QuerySet represents a collection of database records that you can filter, order, slice, and otherwise manipulate. Importantly, QuerySets are lazy — they don't hit the database until you actually evaluate them.

- **Lazy Evaluation**: the query executes only when the QuerySet is evaluated (iteration, `list()`, etc.).
- **Chainable**: methods can be chained together to build complex queries incrementally.
- **Cached**: once evaluated, results are cached to avoid repeated database hits.
- **Immutable**: each method returns a new QuerySet instance.

```python
# This doesn't hit the database yet
books = Book.objects.filter(genre='Fiction')

# This still doesn't hit the database
books = books.filter(is_available=True)

# This hits the database
for book in books:  # QuerySet is evaluated here
    print(book.title)
```

### The Manager: Your Gateway to the Database

Every Django model has at least one manager, accessible through the `objects` attribute — the interface through which you perform database queries.

### Creating Records

**Method 1 — `save()`:**

```python
book = Book(
    title="The Catcher in the Rye",
    isbn="9780316769488",
    author=author_instance,
    publication_date="1951-07-16",
    genre="F",
    pages=234,
    summary="A novel about teenage rebellion and alienation.",
    language="English"
)
book.save()
```

**Method 2 — `create()`:**

```python
book = Book.objects.create(
    title="To Kill a Mockingbird",
    isbn="9780061120084",
    author=author_instance,
    publication_date="1960-07-11",
    genre="F",
    pages=336,
    summary="A novel about racial injustice in the American South.",
    language="English"
)
```

**Method 3 — `get_or_create()`:**

```python
book, created = Book.objects.get_or_create(
    isbn="9780451524935",
    defaults={
        'title': "Nineteen Eighty-Four",
        'author': author_instance,
        'publication_date': "1949-06-08",
        'genre': "SF",
        'pages': 328,
        'summary': "A dystopian social science fiction novel.",
        'language': "English"
    }
)
if created:
    print(f"Created new book: {book.title}")
else:
    print(f"Retrieved existing book: {book.title}")
```

**Method 4 — `update_or_create()`:**

```python
book, created = Book.objects.update_or_create(
    isbn="9780061120084",
    defaults={'rating': 5, 'is_available': True}
)
```

### Retrieving Records: The QuerySet API

**Retrieving all records:**

```python
all_books = Book.objects.all()
recent_books = Book.objects.all().order_by('-publication_date')[:10]
```

**Retrieving a single record:**

```python
book = Book.objects.get(pk=1)
book = Book.objects.get(isbn="9780451524935")
book = Book.objects.first()
book = Book.objects.last()
```

**Important**: `get()` raises `DoesNotExist` if no record matches, and `MultipleObjectsReturned` if more than one matches. Use it only when exactly one match is expected.

**Retrieving with `filter()`:**

```python
fiction_books = Book.objects.filter(genre='F')
available_fiction = Book.objects.filter(genre='F', is_available=True)
highly_rated = Book.objects.filter(rating__gte=4)
recent_books = Book.objects.filter(publication_date__year=2023)
```

**Retrieving with `exclude()`:**

```python
non_fiction = Book.objects.exclude(genre='F')
available_not_long = Book.objects.filter(is_available=True).exclude(pages__gt=500)
```

### Field Lookups

Field lookups use a double underscore (`__`) to separate the field name from the lookup type.

| Lookup | Description | Example |
|---|---|---|
| `exact` | Exact match (default) | `title__exact='Django'` |
| `iexact` | Case-insensitive exact match | `title__iexact='django'` |
| `contains` / `icontains` | Contains the string | `title__icontains='django'` |
| `startswith` / `istartswith` | Starts with | `title__startswith='The'` |
| `endswith` / `iendswith` | Ends with | `title__endswith='Django'` |
| `gt` / `gte` | Greater than / or equal | `pages__gt=300` |
| `lt` / `lte` | Less than / or equal | `rating__lte=2` |
| `in` | In a list | `genre__in=['F','SF']` |
| `range` | Between two values | `pages__range=(100,300)` |
| `isnull` | Is NULL | `publisher__isnull=True` |
| `year` / `month` / `day` | Date part of a field | `publication_date__year=2023` |
| `week_day` | Day of the week (1=Sunday) | `publication_date__week_day=1` |
| `regex` / `iregex` | Regular expression match | `title__regex=r'^The.*Django$'` |

```python
# Books published in 2023 with "Django" in the title
books = Book.objects.filter(
    publication_date__year=2023,
    title__icontains='Django'
)

# Books with more than 300 pages OR published before 2000
books = Book.objects.filter(
    models.Q(pages__gt=300) | models.Q(publication_date__year__lt=2000)
)

# Books with no publisher
books = Book.objects.filter(publisher__isnull=True)
```

### Chaining QuerySet Methods

```python
queryset = Book.objects.all()
queryset = queryset.filter(genre='F')
queryset = queryset.filter(is_available=True)
queryset = queryset.order_by('-rating')
queryset = queryset[:10]

top_fiction_books = queryset  # single optimized query, executed on evaluation
```

### Slicing and Ordering

```python
# Ordering
books = Book.objects.order_by('title')                 # ascending
books = Book.objects.order_by('-publication_date')      # descending
books = Book.objects.order_by('genre', '-rating')        # multiple fields

# Slicing
first_five = Book.objects.all()[:5]
next_ten = Book.objects.all()[5:15]
best_book = Book.objects.order_by('-rating')[0]
```

**Note**: negative indexing (`[-1]`) is not supported for QuerySets — use `last()` instead.

### Updating Records

**Individual objects with `save()`:**

```python
book = Book.objects.get(pk=1)
book.title = "The Great Gatsby - Revised Edition"
book.rating = 5
book.save()
```

**Bulk updates with `update()`:**

```python
Book.objects.filter(genre='F').update(is_available=False)
Book.objects.filter(pages__gt=500).update(is_available=False, rating=3)
```

**Important**: `update()` doesn't call `save()` on individual objects, so signals and custom `save()` methods aren't triggered — use it for performance when those hooks aren't needed.

### Deleting Records

```python
# Individual
book = Book.objects.get(pk=1)
book.delete()

# Bulk
Book.objects.filter(rating__isnull=True).delete()
Book.objects.filter(publication_date__year__lt=1950).delete()
```

By default, Django cascades deletion to related objects unless you've specified `on_delete=models.PROTECT`.

### Advanced Queries

**Q Objects for complex logic (OR, AND, NOT):**

```python
from django.db.models import Q

books = Book.objects.filter(Q(genre='F') | Q(rating=5))
books = Book.objects.filter(Q(genre='F') & Q(rating=5))
books = Book.objects.filter(~Q(genre='F'))
books = Book.objects.filter(Q(genre='F') | Q(genre='NF', rating=5))
```

**F Objects for field comparisons:**

```python
from django.db.models import F

# Increment borrowed_count by 1
Book.objects.filter(pk=1).update(borrowed_count=F('borrowed_count') + 1)
```

**Aggregation and Annotation:**

```python
from django.db.models import Count, Sum, Avg, Max, Min

genre_counts = Book.objects.values('genre').annotate(count=Count('id'))
total_pages = Book.objects.aggregate(Sum('pages'))
avg_rating = Book.objects.aggregate(Avg('rating'))

stats = Book.objects.aggregate(
    total_books=Count('id'),
    avg_pages=Avg('pages'),
    max_pages=Max('pages'),
    min_pages=Min('pages'),
    total_borrowed=Sum('borrowed_count')
)
```

### Working with Dates

```python
from datetime import date, timedelta
from django.utils import timezone

today_books = Book.objects.filter(publication_date=date.today())
this_year_books = Book.objects.filter(publication_date__year=date.today().year)

thirty_days_ago = timezone.now().date() - timedelta(days=30)
recent_books = Book.objects.filter(publication_date__gte=thirty_days_ago)

december_books = Book.objects.filter(publication_date__month=12)
```

### Performance Optimizations

**1. `select_related()` for foreign keys** — avoids N+1 queries via a JOIN:

```python
# Without select_related: N+1 queries
for book in Book.objects.all():
    print(book.author.last_name)

# With select_related: 1 query
for book in Book.objects.select_related('author'):
    print(book.author.last_name)
```

**2. `prefetch_related()` for many-to-many and reverse foreign keys:**

```python
authors = Author.objects.prefetch_related('books')
for author in authors:
    print(author.books.all())  # Already preloaded
```

**3. `only()` and `defer()` to limit fields:**

```python
books = Book.objects.only('title', 'author')
books = Book.objects.defer('summary')
```

**4. `count()` instead of `len()`:**

```python
total = Book.objects.count()  # SELECT COUNT(*) — efficient
```

**5. `exists()` instead of evaluating truthiness:**

```python
if Book.objects.filter(title__icontains='Django').exists():
    print("Found books")
```

### Working with QuerySets: Advanced Techniques

A QuerySet is evaluated when you iterate over it, call `list()` on it, slice with an explicit step, call `bool()` or `len()` on it, or call `repr()`/`str()`.

```python
# Inspect the SQL generated
print(books.query)

from django.db import connection
print(connection.queries[-1]['sql'])

# Combining QuerySets (same model only)
fiction_books = Book.objects.filter(genre='F')
high_rated_books = Book.objects.filter(rating__gte=4)
combined_union = fiction_books | high_rated_books
combined_intersection = fiction_books & high_rated_books
```

### A Complete Example

```python
from datetime import date, timedelta
from django.db.models import Q, Count, Avg, Sum
from library.models import Book, Author

# CREATE
author, created = Author.objects.get_or_create(
    first_name="Harper", last_name="Lee",
    defaults={'birth_date': date(1926, 4, 28),
              'biography': "American novelist best known for To Kill a Mockingbird."}
)

book = Book.objects.create(
    title="To Kill a Mockingbird", subtitle="A Novel",
    isbn="9780061120084", author=author,
    publication_date=date(1960, 7, 11), genre="F", pages=336,
    summary="The story of young Scout Finch and her father, Atticus.",
    language="English", rating=5
)

# READ
fiction_books = Book.objects.filter(genre='F')
available_fiction = Book.objects.filter(genre='F', is_available=True).order_by('title')
django_books = Book.objects.filter(title__icontains='Django')
best_available = Book.objects.filter(is_available=True).order_by('-rating').first()
genre_counts = Book.objects.values('genre').annotate(count=Count('id'))

# UPDATE
book.rating = 4
book.save()
Book.objects.filter(author=author).update(is_available=True)

# DELETE
book.delete()
Book.objects.filter(rating__isnull=True).delete()

# COMPLEX QUERIES
last_year = date.today() - timedelta(days=365)
recent_high_rated = Book.objects.filter(
    publication_date__gte=last_year, is_available=True, rating__gte=4
)

# PERFORMANCE
authors_with_books = Author.objects.prefetch_related('books')
books = Book.objects.select_related('author', 'publisher')
```

### Summary

- QuerySets: the foundation of Django's ORM, representing collections of records.
- Creating records with `create()`, `save()`, `get_or_create()`, and `update_or_create()`.
- Retrieving with `all()`, `get()`, `filter()`, and `exclude()`, plus field lookups.
- Ordering and slicing results.
- Updating and deleting, individually and in bulk.
- Advanced queries with `Q` and `F` objects, aggregation, and annotation.
- Performance optimizations: `select_related()`, `prefetch_related()`, `only()`, `defer()`, `count()`, `exists()`.
- Evaluating and debugging QuerySets.

---

## 2.7 Model Relationships: Connecting Your Data

Real-world applications rarely deal with isolated pieces of data. Books have authors, authors write multiple books, books belong to publishers. These connections are called relationships, and they are the foundation of relational databases.

### Understanding Database Relationships

- **One-to-Many (or Many-to-One)**: one author writes many books; each book has one author. Implemented with `ForeignKey`.
- **Many-to-Many**: a book can have many authors, an author can write many books. Implemented with `ManyToManyField`.
- **One-to-One**: a user has one profile; a profile belongs to one user. Implemented with `OneToOneField`.

### 2.7.1 ForeignKey: One-to-Many Relationships

`ForeignKey` is the workhorse of Django's relationship system, creating a many-to-one relationship.

```python
from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # ... other fields ...

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    # ... other fields ...

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='books')
    publication_date = models.DateField()
    genre = models.CharField(max_length=50)
    pages = models.IntegerField()
    summary = models.TextField()

    def __str__(self):
        return self.title
```

### Understanding on_delete

| Option | Behavior | Use Case |
|---|---|---|
| `CASCADE` | Delete all related objects | Parent can't exist without children |
| `PROTECT` | Prevent deletion if related objects exist | Preserve historical data |
| `RESTRICT` | Restrict deletion (Django 3.1+) | Similar to PROTECT, different implementation |
| `SET_NULL` | Set the FK to NULL (needs `null=True`) | Optional relationship |
| `SET_DEFAULT` | Set the FK to a default value | A fallback default exists |
| `SET()` | Set to a specific value or callable | Custom behavior |
| `DO_NOTHING` | Do nothing (may cause integrity errors) | Rarely used |

### Understanding related_name

`related_name` gives a way to access related objects from the other side of the relationship.

```python
class Book(models.Model):
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books'  # Custom reverse name
    )
    # Now: author.books.all() instead of the default author.book_set.all()
```

Use `related_name` for readability, to avoid conflicts, or when a model has multiple foreign keys to the same target:

```python
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                                related_name='authored_books')
    editor = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='edited_books')

# author.authored_books.all()  # Books authored by this person
# author.edited_books.all()    # Books edited by this person
```

### Querying with Foreign Keys

**Forward queries** (from the model with the ForeignKey):

```python
harper_lee = Author.objects.get(last_name='Lee', first_name='Harper')
books = Book.objects.filter(author=harper_lee)
books = Book.objects.filter(author__last_name='Lee')
books = Book.objects.filter(publisher__country='US')
```

**Reverse queries** (from the model without the ForeignKey):

```python
author = Author.objects.get(pk=1)
books = author.books.all()
recent_books = author.books.filter(publication_date__year=2023)
book_count = author.books.count()
```

### Creating Objects with Foreign Keys

```python
# Assign the object directly
book = Book(title="New Book", isbn="1234567890123", author=author, ...)
book.save()

# Assign by primary key
book = Book(title="New Book", isbn="1234567890123", author_id=1, ...)
book.save()

# Through the reverse relationship manager
book = author.books.create(title="New Book", isbn="1234567890123", ...)

# get_or_create via the reverse manager
book, created = author.books.get_or_create(
    isbn="1234567890123",
    defaults={'title': "New Book", ...}
)
```

### Updating and Deleting with Foreign Keys

```python
# Change the author of a book
book = Book.objects.get(pk=1)
book.author = Author.objects.get(pk=2)
book.save()

# Delete all books by an author
author.books.all().delete()

# Delete the author (cascades to books if on_delete=CASCADE)
author.delete()
```

### Advanced Foreign Key Features

`select_related()` performs a JOIN to retrieve related objects in a single query, avoiding the N+1 query problem:

```python
books = Book.objects.select_related('author', 'publisher')
for book in books:
    print(book.author.last_name)
    print(book.publisher.name)

# Chaining across levels
books = Book.objects.select_related('author', 'author__profile__address')
```

### 2.7.2 ManyToManyField: Many-to-Many Relationships

Many-to-many relationships occur when multiple records in one table can relate to multiple records in another — for example, co-authored books.

```python
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(
        Author,
        related_name='books',
        through='BookAuthor',
        through_fields=('book', 'author'),
    )

    def __str__(self):
        return self.title


class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    contribution_type = models.CharField(
        max_length=50,
        choices=[('A', 'Author'), ('E', 'Editor'), ('C', 'Contributor'), ('F', 'Foreword')],
        default='A'
    )
    contribution_order = models.IntegerField(default=1)

    class Meta:
        ordering = ['contribution_order']
        unique_together = [['book', 'author']]
```

### The Through Model

The `through` parameter creates a custom intermediary table, useful when the relationship itself has additional attributes, metadata, or validation needs.

Without a `through` model, Django creates a simple junction table automatically with `book_id` and `author_id` columns.

### Querying with ManyToMany Fields

```python
# Forward
author = Author.objects.get(pk=1)
books = Book.objects.filter(authors=author)
books = Book.objects.filter(authors__last_name='Lee')

from django.db.models import Count
books = Book.objects.annotate(author_count=Count('authors')).filter(author_count__gte=2)

# Reverse
books = author.books.all()
recent_books = author.books.filter(publication_date__year=2023)

# Through the through model directly
contributions = BookAuthor.objects.filter(book=book)
editors = BookAuthor.objects.filter(contribution_type='E')
```

### Creating and Managing Many-to-Many Relationships

```python
# add()
book.authors.add(author1, author2)
book.authors.add(*author_ids)

# via the through model directly
BookAuthor.objects.create(book=book, author=author, contribution_type='A', contribution_order=1)

# set() — replace all existing
book.authors.set(author_ids)

# remove() and clear()
book.authors.remove(author1, author2)
book.authors.clear()
```

**Important**: with a custom through model that has required extra fields, you cannot use `add()`/`set()` directly for those fields — create through-model instances explicitly instead.

### Performance Optimizations for Many-to-Many Relationships

```python
# Without prefetch_related: N+1 queries
for book in Book.objects.all():
    print(book.authors.all())

# With prefetch_related: 2 queries total
for book in Book.objects.prefetch_related('authors'):
    print(book.authors.all())

# Prefetch with filtering
from django.db.models import Prefetch

books = Book.objects.prefetch_related(
    Prefetch('authors',
             queryset=Author.objects.filter(birth_date__year__gt=1900),
             to_attr='modern_authors')
)
```

### 2.7.3 OneToOneField: One-to-One Relationships

One-to-one relationships are used when one record relates to exactly one record in another table — e.g., a user and their profile.

```python
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


# Forward
profile = UserProfile.objects.get(user=user)

# Reverse
user = User.objects.get(username='johndoe')
profile = user.profile

if hasattr(user, 'profile'):
    profile = user.profile
else:
    profile = UserProfile.objects.create(user=user, bio="New user")
```

### 2.7.4 Advanced Relationship Features

**Recursive Relationships** — a model relating to itself, common in hierarchies:

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )

    def __str__(self):
        return self.name
```

**Generic Relationships** — pointing to any model via Django's content types framework:

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


# Usage
book = Book.objects.get(pk=1)
comment = Comment.objects.create(content="Great book!", content_object=book)
```

**Subquery and Exists Expressions:**

```python
from django.db.models import OuterRef, Subquery, Exists, Count

latest_books = Book.objects.filter(author=OuterRef('pk')).order_by('-publication_date')
authors = Author.objects.annotate(latest_book_title=Subquery(latest_books.values('title')[:1]))

authors = Author.objects.annotate(book_count=Count('books')).filter(book_count__gte=3)

# Authors who have published at least one book
authors = Author.objects.filter(Exists(Book.objects.filter(author=OuterRef('pk'))))
```

### 2.7.5 Relationship Best Practices

- Choose the right type: `ForeignKey` (one-to-many), `ManyToManyField` (many-to-many), `OneToOneField` (one-to-one).
- Always set `on_delete` — it's required and ensures data integrity.
- Use `related_name` for clarity and to prevent conflicts.
- Django automatically indexes foreign keys, improving performance.
- Optimize with `select_related()` (foreign keys) and `prefetch_related()` (many-to-many, reverse FKs).
- Use `through` models when the relationship needs extra data or validation.
- Be mindful of query performance: `only()`, `defer()`, `values()`, `exists()`, `count()`.
- Plan relationships early — they're central to your data model and hard to change later.

### 2.7.6 Complete Example: A Library with Relationships

Bringing it all together — authors, publishers, genres, a through model, books, copies, and reviews:

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    established = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                                null=True, blank=True, related_name='subgenres')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class BookAuthor(models.Model):
    CONTRIBUTION_CHOICES = [
        ('A', 'Author'), ('E', 'Editor'), ('C', 'Contributor'),
        ('F', 'Foreword'), ('I', 'Introduction'), ('T', 'Translator'),
    ]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    contribution_type = models.CharField(max_length=1, choices=CONTRIBUTION_CHOICES, default='A')
    contribution_order = models.IntegerField(default=1)
    royalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['contribution_order']
        unique_together = [['book', 'author', 'contribution_type']]

    def __str__(self):
        return f"{self.author} - {self.get_contribution_type_display()} of {self.book}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    authors = models.ManyToManyField(Author, through=BookAuthor, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='books')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='books')
    publication_date = models.DateField()
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=50, default='English')
    summary = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    borrowed_count = models.IntegerField(default=0)
    rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def full_title(self):
        return f"{self.title}: {self.subtitle}" if self.subtitle else self.title

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return None

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['is_available']),
        ]


class BookCopy(models.Model):
    CONDITION_CHOICES = [('E', 'Excellent'), ('G', 'Good'), ('F', 'Fair'), ('P', 'Poor'), ('D', 'Damaged')]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='copies')
    copy_number = models.PositiveIntegerField()
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES, default='G')
    location = models.CharField(max_length=100, blank=True)
    is_borrowed = models.BooleanField(default=False)
    borrowed_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='borrowed_copies')
    borrowed_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Copy #{self.copy_number} of {self.book.title}"

    class Meta:
        ordering = ['book', 'copy_number']
        unique_together = [['book', 'copy_number']]


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review of {self.book.title} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        unique_together = [['book', 'user']]
```

### Summary

- `ForeignKey`: one-to-many relationships, `on_delete` behaviors, `related_name`, and querying.
- `ManyToManyField`: many-to-many relationships, `through` models, and querying.
- `OneToOneField`: one-to-one relationships and their use cases.
- Advanced features: recursive relationships, generic relationships, subqueries, and exists.
- Best practices for choosing relationship types, optimizing queries, and planning your data model.

---

## 2.8 Advanced Model Features

Django's ORM offers much more beneath the surface. In this section, we explore model inheritance, custom managers and querysets, custom model methods, signals, and other advanced techniques used to build robust applications.

### 2.8.1 Model Inheritance

Django supports three types of model inheritance, each with different use cases and trade-offs.

**Abstract Base Classes** — used to share common fields or methods across multiple models without creating a table for the parent.

```python
from django.db import models


class TimestampedModel(models.Model):
    """Abstract base class that adds created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This makes it an abstract base class


class Book(TimestampedModel):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    # ... other fields ...


class Author(TimestampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # ... other fields ...

# Both models get created_at/updated_at, but no 'timestampedmodel' table exists
```

Another example — a soft-delete pattern:

```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: mark as deleted instead of removing from database."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def deleted(self):
        return super().get_queryset().filter(is_deleted=True)

    def all_with_deleted(self):
        return super().get_queryset()
```

Abstract base classes can also define `Meta` options (ordering, indexes) that child classes inherit.

**Multi-Table Inheritance** — creates a database table for both parent and child models, with an implicit `OneToOneField` from child to parent.

```python
class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(blank=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Author(Person):
    """An author is a person who writes books."""
    pen_name = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    website = models.URLField(blank=True)


class Editor(Person):
    """An editor is a person who edits books."""
    specialization = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    years_experience = models.IntegerField(default=0)
```

Django creates three tables (`person`, `author`, `editor`); querying `Author` joins `author` and `person` under the hood.

```python
# Optimize with select_related to avoid a join per iteration
authors = Author.objects.select_related('person_ptr')
for author in authors:
    print(author.first_name)  # Already loaded
```

**Proxy Models** — change a model's behavior (methods, default ordering) without changing the database schema.

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    is_available = models.BooleanField(default=True)
    rating = models.IntegerField(default=3)


class AvailableBook(Book):
    """Proxy model that changes ordering and adds a method."""

    class Meta:
        proxy = True
        ordering = ['-rating']

    def days_since_publication(self):
        from django.utils import timezone
        return (timezone.now().date() - self.publication_date).days

# Proxy models don't filter automatically at the database level;
# you must still filter manually:
available_books = AvailableBook.objects.filter(is_available=True)
```

Proxy models are particularly useful for providing different admin views of the same underlying data.

**Choosing the Right Inheritance Pattern:**

| Pattern | Use Case | Database Impact |
|---|---|---|
| Abstract Base Class | Share fields/methods, no table for parent | No additional tables |
| Multi-Table Inheritance | Parent and child both need tables | Separate tables, join required |
| Proxy Model | Change behavior, same schema | No database changes |

### 2.8.2 Custom Managers and QuerySets

As your application grows, you'll often repeat the same filters. Custom managers let you encapsulate these patterns.

```python
from django.db import models


class BookManager(models.Manager):
    def available(self):
        return self.get_queryset().filter(is_available=True)

    def high_rated(self, threshold=4):
        return self.get_queryset().filter(rating__gte=threshold)

    def recent(self, days=30):
        from django.utils import timezone
        cutoff = timezone.now().date() - timezone.timedelta(days=days)
        return self.get_queryset().filter(publication_date__gte=cutoff)


class Book(models.Model):
    title = models.CharField(max_length=200)
    # ... other fields ...
    objects = BookManager()

# Chaining
books = Book.objects.available().high_rated(4).recent(30)
```

For more advanced functionality, create a custom QuerySet class and use it as the manager:

```python
class BookQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_available=True)

    def high_rated(self, threshold=4):
        return self.filter(rating__gte=threshold)

    def get_top_rated(self, limit=10):
        return self.order_by('-rating', 'title')[:limit]


class BookManager(models.Manager.from_queryset(BookQuerySet)):
    """Manager that returns the custom QuerySet from all methods."""
    pass


class Book(models.Model):
    # ... fields ...
    objects = BookManager()

# All chained methods now return BookQuerySet
books = Book.objects.available().by_genre('Fiction').get_top_rated(5)
```

**Common Manager Patterns** — the "Active" pattern:

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Article(models.Model):
    title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()          # default: returns all
    active_objects = ActiveManager()    # custom: returns only active
```

### 2.8.3 Custom Model Methods

Instance methods add business logic tied to a single object:

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    # ... other fields ...

    def can_be_borrowed(self):
        return self.is_available and self.copies.filter(is_borrowed=False).exists()

    def borrow(self, user):
        available_copy = self.copies.filter(is_borrowed=False).first()
        if not available_copy:
            raise ValueError(f"No available copies of {self.title}")

        from django.utils import timezone
        available_copy.is_borrowed = True
        available_copy.borrowed_by = user
        available_copy.borrowed_date = timezone.now().date()
        available_copy.due_date = timezone.now().date() + timezone.timedelta(days=14)
        available_copy.save()

        self.borrowed_count += 1
        self.save()
        return available_copy

    @property
    def age(self):
        """Property: age of the book in years."""
        from django.utils import timezone
        return (timezone.now().date() - self.publication_date).days // 365
```

Class methods operate on the model class itself:

```python
class Book(models.Model):
    # ... fields ...

    @classmethod
    def get_or_create_from_isbn(cls, isbn, defaults=None):
        try:
            return cls.objects.get(isbn=isbn), False
        except cls.DoesNotExist:
            book_data = cls._fetch_book_data(isbn)
            if defaults:
                book_data.update(defaults)
            return cls.objects.create(**book_data), True

    @classmethod
    def count_by_genre(cls):
        from django.db.models import Count
        return cls.objects.values('genre').annotate(count=Count('id'))
```

### 2.8.4 Signals

Django signals let you execute code when certain actions occur on your models. They're powerful but should be used judiciously.

Common signals: `pre_save` / `post_save`, `pre_delete` / `post_delete`, `pre_migrate` / `post_migrate`, and `m2m_changed`.

```python
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver


@receiver(pre_save, sender=Book)
def book_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        print(f"Creating new book: {instance.title}")


@receiver(post_save, sender=Book)
def book_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"Book '{instance.title}' was created!")


@receiver(m2m_changed, sender=Book.authors.through)
def book_authors_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        names = model.objects.filter(pk__in=pk_set).values_list('full_name', flat=True)
        print(f"Authors {', '.join(names)} added to '{instance.title}'")
```

Keep signals organized in a separate `signals.py`, and connect them via the app's `ready()` method:

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, BookCopy


@receiver(post_save, sender=BookCopy)
def update_book_availability(sender, instance, **kwargs):
    book = instance.book
    available_copies = book.copies.filter(is_borrowed=False)
    book.is_available = available_copies.exists()
    book.save()
```

```python
# apps.py
from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        import library.signals
```

- Keep signal handlers simple — offload heavy work to background tasks.
- Handle exceptions so signal failures don't break the main operation.
- Use specific senders and avoid circular dependencies between signals.
- Test your signal handlers.

### 2.8.5 Database Constraints

**Unique constraints:**

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author')
        ]
```

**Check constraints:**

```python
class Book(models.Model):
    pages = models.IntegerField()
    rating = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(pages__gte=1), name='pages_positive'),
            models.CheckConstraint(
                check=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='rating_range'
            ),
        ]
```

**Conditional unique constraints:**

```python
class BookCopy(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    copy_number = models.IntegerField()
    is_borrowed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'copy_number'],
                condition=models.Q(is_borrowed=False),
                name='unique_available_copy'
            )
        ]
```

### 2.8.6 Indexes

```python
class Book(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    author = models.CharField(max_length=100)
    publication_date = models.DateField()
    genre = models.CharField(max_length=50)

    class Meta:
        indexes = [
            models.Index(fields=['author', 'publication_date']),
            models.Index(fields=['genre'], name='genre_idx'),
            models.Index(fields=['-publication_date']),
        ]
```

Django also supports conditional indexes, limited to rows matching a condition — useful for indexing only "active" or "available" subsets of a table.

### 2.8.7 Custom Field Types

When Django's built-in fields aren't enough, you can create your own. Note: Django 3.1+ already includes a built-in `JSONField` for supported databases.

```python
from django.db import models


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = models.JSONField(default=dict)  # Django 3.1+
```

### 2.8.8 Model Meta Options Recap

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    # ... fields ...

    class Meta:
        ordering = ['-publication_date', 'title']
        get_latest_by = 'publication_date'
        verbose_name = "Book"
        verbose_name_plural = "Books"
        db_table = 'library_books'
        constraints = [...]
        indexes = [...]
        permissions = [
            ('can_publish_book', 'Can publish books'),
            ('can_unpublish_book', 'Can unpublish books'),
        ]
        default_manager_name = 'objects'
```

### Summary

- **Model Inheritance**: abstract base classes, multi-table inheritance, and proxy models.
- **Custom Managers and QuerySets**: encapsulating complex queries and business logic.
- **Custom Model Methods**: instance methods, class methods, and properties.
- **Signals**: reacting to model events without tight coupling.
- **Database Constraints and Indexes**: enforcing integrity and optimizing performance.
- **Custom Fields and Meta options** for fine-tuning your models.

---

## 2.9 Chapter Summary and What's Next

We've reached the end of Chapter 2, and what a journey it's been. We've transformed from developers who could only create static pages to ones who can design sophisticated, data-driven applications.

### Chapter Recap

- **2.1** — The role of relational databases, the ORM, and how models map to tables.
- **2.2** — Configuring SQLite, PostgreSQL, and MySQL, and managing credentials with environment variables.
- **2.3** — Field types, field options, `__str__()`, the `Meta` class, choices, and validation.
- **2.4** — The migration workflow, migration files, data migrations, squashing, and troubleshooting.
- **2.5** — Activating and customizing the admin interface: `ModelAdmin`, inlines, actions, and security.
- **2.6** — QuerySets, CRUD operations, field lookups, Q/F objects, aggregation, and performance optimization.
- **2.7** — `ForeignKey`, `ManyToManyField`, and `OneToOneField` relationships, and querying across them.
- **2.8** — Model inheritance, custom managers/querysets, custom methods, signals, constraints, and indexes.

### Key Takeaways

- Models are the foundation of your application — well-designed models make everything else easier.
- Migrations give you version control for your database schema.
- The ORM saves time, catches errors, and handles security for you.
- Relationships are powerful — use the right type for each situation.
- The admin interface is a killer feature, providing a full-featured CMS out of the box.
- Performance matters — use `select_related()`, `prefetch_related()`, and indexes appropriately.
- Encapsulate business logic using custom managers, methods, and signals.

### Looking Ahead: Chapter 3 — Views and Templates

Now that you've mastered the data layer, it's time to connect it to the user interface. In Chapter 3, we'll explore:

- **Class-Based Views**: building views that are more powerful and reusable.
- **Generic Views**: leveraging Django's built-in views for common patterns.
- **Template Inheritance**: building consistent, maintainable templates.
- **Context Processors**: making data available across templates.
- **Forms**: handling user input with validation and security.
- **Template Tags and Filters**: extending Django's templating language.

### Practice Projects

- **A Blog System**: with posts, authors, categories, and comments.
- **A Library Management System**: with books, authors, publishers, and borrowing.
- **An E-commerce Product Catalog**: with products, categories, and inventory.

Each of these projects will reinforce the concepts you've learned and give you practical experience.

### Final Words

You've completed one of the most important chapters in your Django journey. You now understand the heart of Django — its ORM and data layer. This knowledge will serve you throughout your career, whether you're building simple websites or complex enterprise applications.

Remember: the best way to learn is to build. Take what you've learned and start building something real. Make mistakes, break things, and fix them. That's how you truly master the craft.

In the next chapter, we'll bring your data to life by connecting it to views and templates. See you there!
