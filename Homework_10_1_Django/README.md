# Django Bookstore

A server-rendered bookstore application built with Django. Visitors can browse
and search a book catalog, manage a session-based shopping cart, place orders,
and begin card payments through Stripe Checkout. The project includes account
registration and permission-protected catalog management.

## Project Overview

The Django project package is `homework_10_1_django`, and the bookstore
application is `my_app`. The application uses PostgreSQL for persistent data
and Redis for Django's cache when running with the default settings. Docker
Compose defines the web, PostgreSQL, and Redis services.

The site is mounted at `/books/`. The project also supports English and
Ukrainian translations.

## Features

- Browse book listings with pagination and case-insensitive title search.
- View book details and asynchronous book/category reports.
- Register, log in, and log out of a custom user account.
- Create, update, and delete books with the corresponding Django permissions.
- Add books to a session-based cart, update quantities, remove items, and
  clear the cart.
- Create orders from cart contents and send an order confirmation email.
- Start Stripe Checkout for an order.
- Run the application with Docker Compose, PostgreSQL, and Redis.
- Run tests with pytest against an in-memory SQLite database.

## Requirements

- Python 3.12
- PostgreSQL (for running Django outside Docker)
- Redis (for running Django outside Docker with the default cache settings)
- Docker Desktop with the Docker Compose plugin (for the containerized setup)

## Setup and Installation

### Configure environment variables

Create a `.env` file in the project root. Do not commit real credentials.
For Docker Compose, use the service name `db` for `DB_HOST`:

```dotenv
SECRET_KEY=replace-with-a-long-random-secret
DB_NAME=bookstore
DB_USER=bookstore
DB_PASSWORD=replace-with-a-strong-password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
STRIPE_PUBLISHABLE_KEY=pk_test_replace_me
STRIPE_SECRET_KEY=sk_test_replace_me
```

The Stripe keys are only needed to create payment sessions; use Stripe test
credentials during development. For security, use your own generated Django
secret key and never publish passwords, secret keys, or production payment
credentials.

### Run with Docker Compose

From the project root, build and start the application and its dependencies:

```powershell
docker compose up --build
```

The web container applies database migrations, collects static files, and
starts Django on port `8000`. Open <http://localhost:8000/books/>. Create an
administrator account in another terminal with:

```powershell
docker compose exec web python manage.py createsuperuser
```

The PostgreSQL data is stored in the Compose-managed `postgres_data` volume and
is retained when containers are stopped. Stop the services with
`docker compose down`.

### Run Django locally with PostgreSQL and Redis

Start PostgreSQL and Redis separately, install Python dependencies, and
configure the environment. The database and cache hosts must be reachable from
the host machine. When using the Compose database and Redis services while
running Django on the host, change `DB_HOST` in `.env` to `localhost` and set
`REDIS_URL=redis://localhost:6379/1`. Set `DB_HOST=db` and the Compose Redis
URL again when running the web service in Docker.

In PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/books/>. On systems where `py -3.12` is not
available, create the virtual environment with the installed Python 3.12
executable.

## Running Tests

Install the development dependencies and run the test suite from the project
root:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

The pytest configuration uses the project's test settings, which use an
in-memory SQLite database and a local in-memory cache. Coverage is enabled by
the test configuration.

## Project Structure

```text
homework_10_1_django/   Django settings and project URL configuration
my_app/                Bookstore models, views, forms, cart, and tests
templates/             HTML templates for books, cart, and orders
static/                Project static assets
locale/                English and Ukrainian translation catalogs
Dockerfile             Django web image definition
docker-compose.yaml    Web, PostgreSQL, and Redis services
```

## AI Usage

Document how AI was used in this project:

- **Code Review:** Prompt:

  **Role:** Senior Django Developer and Security Expert.  
  **Context:** A Django Bookstore e-commerce application with session-based
  carts, custom models, Stripe Checkout, and
  email notifications.  
  **Task:** Review `order_create`, `payment_process`, and the three async views
  in `my_app/views.py` for bugs, security concerns, performance bottlenecks,
  and Django best-practice issues. Provide concrete recommendations and
  refactored code where appropriate.  
  **Constraints:** Be concise and focus on PEP 8, Django ORM usage, and
  transaction safety. Do not rewrite working logic unnecessarily. Make
  application-code changes only in `my_app/views.py`; do not modify other
  application files. Save the review, including the original code,
  recommendations, and final code for each reviewed view, in `AI_REVIEW.md`(For 
  each of the 3 views/serializers, provide three clearly separated sections: 
  "Original Code", "AI Recommendations" (bullet points explaining why), and 
  "Refactored Final Code".)).  
  **Output:** A Markdown review report in `AI_REVIEW.md`.

  The review identified checkout validation and pricing issues, opportunities
  to reduce order-item database queries, and missing handling for invalid
  payment totals and Stripe errors. The two checkout/payment views were updated
  in `views.py`; the three async report/detail views were reviewed and left
  unchanged. The recommendations and changes are documented in `AI_REVIEW.md`.


- **Tests:** Prompt:

  **Role:** QA Automation Engineer and Python Developer.  
  **Context:**  I have a Django Bookstore project with custom models. 
  I need to write unit tests for the following models to ensure data 
  integrity and correct business logic: [Book, Order, OrderItem] (look up the project).  
  **Task:** Write comprehensive Django unit tests for `Book`, `Order`, and
  `OrderItem` in `my_app/tests/test_models.py`. Cover successful creation,
  string representations, and edge cases such as negative prices and omitted
  optional fields. Include necessary imports and setup methods.
  **Constraints:** The generated tests must be thorough enough to achieve ≥ 60% 
  test coverage for these specific models. Cover successful creation, string 
  representations (str), and edge cases (e.g., negative prices, missing optional fields). 
  Do not implement the solution instantly, write the code here for my review and wait for 
  my decision weather to implement it or not. You MUST include the exact comment 
  "Generated with AI, reviewed and modified inside every test method."
  Add short, clear docstrings to test classes and functions.
  Change only the test file.  
  **Output:** A ready-to-run test file and a coverage report.

  The tests cover model creation and defaults, string representations, order
  totals, item cost calculations, validation, negative prices, and cascade
  deletion. Verification: all 20 tests passed, with 100% coverage of
  `my_app.models`.

- **Documentation:** Prompt:

  **Role:** Python developer and technical writer.  
  **Context:** My Django Bookstore project needs professional documentation 
  and docstrings in views.py file.
  **Task:** Generate PEP 257-compliant English docstrings for all views in
  `views.py` and create a comprehensive, professional `README.md`.  
  **Constraints:** Each view docstring should explain what the view does, its
  arguments, and its return value, using type-hint context when necessary. The
  README should include Project Overview, Features, Setup/Installation
  instructions (including Docker/PostgreSQL when applicable), and an `AI Usage`
  section with Code Review, Tests, and Documentation subsections.  
  **Output:** Documented views and a README checked against the project
  structure and configuration.

  AI assistance added PEP 257-style
  docstrings to the views and drafted this README after reviewing the project
  structure and configuration; the output was checked against the codebase.
