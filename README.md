# Mechanic Shop API

A RESTful Flask API for managing a mechanic shop's **customers**, **mechanics**,
and **service tickets**. Built with the Application Factory Pattern,
SQLAlchemy models mapped from the Mechanic Shop ERD, Marshmallow for
serialization/validation, Swagger (Flasgger) for interactive API
documentation, and a `unittest` test suite covering every route.

## Data Model

- **Customer** — `id`, `name`, `email` (unique), `phone`
- **Mechanic** — `id`, `name`, `email` (unique), `phone`, `address`, `salary`
- **ServiceTicket** — `id`, `VIN`, `service_date`, `service_desc`, `customer_id`

Relationships:

- One customer can have many service tickets (**one-to-many**).
- One service ticket can require multiple mechanics, and one mechanic can
  work multiple tickets (**many-to-many**, via a `service_mechanics`
  junction table).

## Project Structure

```
mechanic-shop-api/
├── flask_app.py                # Entry point — creates the app (WSGI target for gunicorn)
├── config.py                   # Development / Testing / Production configs
├── requirements.txt
├── .env.example                 # Template for local .env (real .env is gitignored)
├── .github/workflows/main.yaml  # CI/CD: build -> test -> deploy to Render
├── application/
│   ├── __init__.py            # create_app() — the Application Factory
│   ├── extensions.py          # db (SQLAlchemy), ma (Marshmallow)
│   ├── models.py              # Customer, Mechanic, ServiceTicket models
│   └── blueprints/
│       ├── customers/         # schema.py + routes.py
│       ├── mechanics/         # schema.py + routes.py
│       └── service_tickets/   # schema.py + routes.py
└── tests/
    ├── test_customers.py
    ├── test_mechanics.py
    └── test_service_tickets.py
```

## Setup

**1. Clone the repo and enter the project folder**

```bash
git clone <your-repo-url>
cd mechanic-shop-api
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
flask --app flask_app run --debug
```

The API will be running at `http://127.0.0.1:5000`. By default it uses a
local SQLite database file (`mechanic_shop.db`, created automatically on
first run) — **no database server setup required.**

### Using MySQL instead of SQLite

The project defaults to SQLite for zero-setup local grading/demoing, but is
config-driven so it's a one-line swap to MySQL (as shown in the lessons):

1. Install the MySQL driver: `pip install mysql-connector-python`
2. Create a database in MySQL Workbench.
3. Set the `DATABASE_URL` environment variable before running:

   ```bash
   # Mac / Linux
   export DATABASE_URL="mysql+mysqlconnector://root:<YOUR MYSQL PASSWORD>@localhost/<YOUR DATABASE>"

   # Windows (PowerShell)
   $env:DATABASE_URL="mysql+mysqlconnector://root:<YOUR MYSQL PASSWORD>@localhost/<YOUR DATABASE>"
   ```

4. Run `python app.py` as usual — tables are created automatically on startup.

## API Documentation (Swagger)

Once the app is running, view the full interactive API documentation
(every route's path, method, tags, parameters, and example
request/response bodies) at:

```
http://127.0.0.1:5000/api/docs/
```

## Endpoints

| Method | Endpoint                                                    | Description                          |
|--------|--------------------------------------------------------------|---------------------------------------|
| POST   | `/customers`                                                 | Create a customer                     |
| GET    | `/customers`                                                  | Get all customers                     |
| GET    | `/customers/<id>`                                             | Get a specific customer               |
| PUT    | `/customers/<id>`                                             | Update a customer                     |
| DELETE | `/customers/<id>`                                             | Delete a customer                     |
| POST   | `/mechanics`                                                  | Create a mechanic                     |
| GET    | `/mechanics`                                                   | Get all mechanics                     |
| GET    | `/mechanics/<id>`                                              | Get a specific mechanic               |
| PUT    | `/mechanics/<id>`                                              | Update a mechanic                     |
| DELETE | `/mechanics/<id>`                                              | Delete a mechanic                     |
| POST   | `/service-tickets`                                             | Create a service ticket (optionally with `mechanic_ids`) |
| GET    | `/service-tickets`                                              | Get all service tickets               |
| GET    | `/service-tickets/<id>`                                         | Get a specific service ticket         |
| PUT    | `/service-tickets/<id>`                                         | Update a service ticket               |
| DELETE | `/service-tickets/<id>`                                         | Delete a service ticket               |
| PUT    | `/service-tickets/<id>/assign-mechanic/<mechanic_id>`           | Assign a mechanic to a ticket         |
| PUT    | `/service-tickets/<id>/remove-mechanic/<mechanic_id>`           | Remove a mechanic from a ticket       |

## Running the Tests

The `tests/` folder has one file per blueprint (`test_customers.py`,
`test_mechanics.py`, `test_service_tickets.py`), each covering every route
plus negative cases (missing fields, duplicate emails, invalid
relationships, 404s). Tests run against an isolated in-memory SQLite
database, so they never touch your real data.

```bash
# Windows
python -m unittest discover tests

# Mac
python3 -m unittest discover tests
```

## Notes

- Validation and serialization are handled by Marshmallow schemas backed
  by `SQLAlchemyAutoSchema`, integrated with the SQLAlchemy models.
- Creating or updating a service ticket accepts an optional `mechanic_ids`
  array to assign mechanics in the same request; the dedicated
  assign-mechanic/remove-mechanic endpoints let you adjust one mechanic at
  a time without resending the whole ticket.
- All routes return standard JSON error bodies (`{"error": "..."}`) with
  the appropriate HTTP status code (400 for validation errors, 404 for
  missing resources).

## Deployment (Render) & CI/CD

This repo is set up to run in production behind `gunicorn`, backed by a
Postgres database hosted on Render, with a GitHub Actions pipeline that
runs the test suite before every deploy.

**One-time Render setup:**

1. Create a **PostgreSQL** instance on Render (free tier is fine) and copy
   its **External Database URL**.
2. Create a **Web Service** on Render pointed at this GitHub repo, and set
   these environment variables in the service's *Environment* tab:
   - `FLASK_CONFIG=production`
   - `DATABASE_URL=<the Postgres External Database URL from step 1>`
   - `SECRET_KEY=<a long random string>`
3. Set the service's **Start Command** to:
   ```
   gunicorn flask_app:app
   ```
4. Turn **Auto-Deploy off** for this service (Settings → Auto-Deploy → No).
   Deploys are triggered by the GitHub Action below instead, so a broken
   build/test never gets auto-deployed to production.
5. Grab the service's **Service ID** (Settings page or the service URL,
   `srv-...`) and create an **API Key** (Account Settings → API Keys).

**One-time GitHub setup:**

In this repo's Settings → Secrets and variables → Actions, add two
repository secrets:

- `RENDER_SERVICE_ID` — the `srv-...` ID from step 5 above
- `RENDER_API_KEY` — the API key from step 5 above

**How it works:** `.github/workflows/main.yaml` defines three jobs —
`build` (installs dependencies to confirm the app installs cleanly),
`test` (runs `python -m unittest discover tests`), and `deploy` (calls
Render's deploy API), each depending on the previous one succeeding. Push
to `main` and GitHub Actions will only deploy to Render if the tests pass.

**Swagger note:** `application/__init__.py`'s `swagger_template` doesn't
hardcode a `host` or `schemes`, so Swagger UI automatically calls the API
at whatever origin actually served the page — no manual edit is needed
after deploying (it'll show `127.0.0.1:5000` locally and your Render URL
in production, both correctly over http/https).

## Submission Checklist

- [ ] Push this code to a **public** GitHub repository (keep it public
      until grading is complete).
- [ ] Confirm the repo's root URL is a valid single GitHub URL (not a
      subfolder, ZIP, or Google Drive link).
- [ ] Record a demo video walking through the project and its
      functionality, and upload it **directly to Disco** (no external
      links).
- [ ] Paste the GitHub repo URL into Disco along with the video.
