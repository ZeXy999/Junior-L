# Chapter 2: Models and Databases

*Designing schemas, evolving them with migrations, and managing data through the built-in admin.*

## Chapter Contents

- 2.2 Configuring Your Database
- 2.3 Defining Models: The Blueprint of Your Data
- 2.4 Migrations: Evolving Your Database Schema
- 2.5 The Django Admin Interface: A Built-In Data Management Tool

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

Let's expand our `Book` model with related models — `Author` and `Publisher` — bringing several concepts together:

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
