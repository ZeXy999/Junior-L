# Junior-L.

Educational programming content and curriculum materials.

## Contents

- [`Django_Chapter1_Foundations.md`](./Django_Chapter1_Foundations.md) — Chapter 1 of a Django course, covering:
  - 1.1 Introduction to Django
  - 1.2 Setting Up Your Django Development Environment
  - 1.3 Understanding the Project Structure and the manage.py Command
  - 1.4 Hello, World! Building Your First View

- [`exercises/django-textbook/`](./exercises/django-textbook) — A working Django project completing the Chapter 1 practical exercises:
  - **Exercise 1 — Personalize Your Greeting**: `/hello/<name>/` renders a personalized greeting (`hello_world/views.py`, `hello_world/urls.py`)
  - **Exercise 2 — About Page**: `/hello/about/` shows a name, bio, and a top-5 favorites list (`hello_world/views.py`, `templates/hello_world/about.html`)
  - **Exercise 3 — Template Tags Practice**: `/hello/numbers/` loops through a list of numbers, flags each as even/odd, and displays their sum (`templates/hello_world/numbers.html`)
  - **Exercise 4 — Template Inheritance**: all pages extend a shared `base.html` with a common header, nav, and footer

  All routes were run and verified against a local dev server before being pushed.

## Library website (this branch)

[`library-project/`](./library-project) is a complete Django library site by Junior: catalog with search and filters, generated book covers, ratings and reviews, borrowing and returns, accounts, admin, a seed command that adds random books, and tests. See [`library-project/README.md`](./library-project/README.md) to run it.
