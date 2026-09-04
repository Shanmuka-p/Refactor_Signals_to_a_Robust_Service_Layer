# Django Signals to Service Layer Refactoring

A production-ready Django application demonstrating the pitfalls of implicit Django Signals and refactoring business logic into an explicit, atomic, and performant Service Layer.

---

## 📌 Project Overview

This project models an e-commerce backend handling **Orders** and aggregated **User Statistics** (`total_spent`, `order_count`). It explores two contrasting architectural patterns:

1. **Implicit Signal Architecture** (Phase 1 & 2): Updates `UserStats` via `post_save` signals on the `Order` model.
2. **Explicit Service Layer Architecture** (Phase 3 & 4): Encapsulates order creation and aggregate calculation inside atomic service functions (`orders.services.create_order`).

---

## 🏗️ Core Architectural Concepts & Pitfalls

### The Dangers of Django Signals
While signals decouple distinct parts of an application, using them for core business logic causes:
* **Spooky Action at a Distance**: Modifying one model implicitly triggers side effects that are hard to trace and debug.
* **Bulk Operation Bypass**: Bulk ORM methods such as `QuerySet.update()`, `QuerySet.delete()`, and `bulk_create()` operate directly in SQL and **bypass Django signals entirely**, causing silent data corruption/inconsistency.
* **Test Isolation Leaks**: Globally registered signals persist across test cases if not explicitly disconnected in test cleanup.

### The Service Layer Solution
Refactoring to `orders.services.create_order`:
* **Explicitness**: Developers know exactly what business logic runs when creating an order.
* **Transaction Safety**: Wrapped in `django.db.transaction.atomic()` to guarantee all-or-nothing database updates.
* **Performance**: Enables bulk insertions (`bulk_create`) and single SQL updates via `F()` expressions.

---

## 🛠️ Project Structure

```text
├── .env.example                # Example environment variables
├── Dockerfile                  # Container definition for Django app
├── docker-compose.yml          # Container orchestration (App + PostgreSQL)
├── manage.py                   # Django CLI entrypoint
├── requirements.txt            # Python dependencies
├── signal_project/             # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── views.py                # Healthcheck endpoint (/)
└── orders/                     # Orders & Statistics application
    ├── apps.py                 # AppConfig setup
    ├── models.py               # Order & UserStats models
    ├── signals.py              # Signal receiver definition (for testing/benchmarks)
    ├── services.py             # Service layer functions (create_order)
    ├── management/
    │   └── commands/
    │       └── benchmark_updates.py # Performance benchmark CLI command
    └── tests/
        ├── test_signals.py     # Tests proving signal bypass and test isolation
        └── test_services.py    # Tests verifying Service Layer correctness
```

---

## 🚀 Environment Variables (`.env.example`)

Copy `.env.example` to `.env` before running:

```bash
SECRET_KEY=django-insecure-placeholder-key
DEBUG=True
POSTGRES_DB=orders_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

---

## 🐳 Docker Setup

Run the application and PostgreSQL database with a single command:

```bash
docker compose up --build
```

Healthchecks will verify that PostgreSQL (`db`) is ready before starting the Django application (`app`), which automatically runs database migrations on startup.

---

## 🧪 Running Unit Tests

Run the full test suite to verify signal bypass behavior, test isolation cleanup, and service layer correctness:

```bash
# Inside Docker container
docker compose exec app python manage.py test

# Local development (with SQLite fallback)
$env:USE_SQLITE="True"; python manage.py test
```

---

## ⚡ Performance Benchmarking

To measure the performance difference between N+1 signal updates vs. bulk Service Layer execution, run:

```bash
python manage.py benchmark_updates
```

### Expected Output Format
```text
Signal approach time: 0.8412s
Optimized service time: 0.0154s
Speedup factor: 54.62x
```