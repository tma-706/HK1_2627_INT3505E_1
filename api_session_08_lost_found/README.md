# Session 08 Homework — AI Lost & Found API Testing

This folder is a minimal, runnable vertical slice of the team project's
AI Lost & Found specification. Its purpose is to provide a realistic API for
Postman/Newman functional tests and Locust load tests.

## Scope

Implemented:

- Signed bearer-token login with two demo users.
- Lost and Found posts with `DRAFT → PUBLISHED` lifecycle.
- Found Post image requirement at publish time.
- Published Lost-to-Found matching with Top 1–10 results.
- Claim creation with private ownership evidence.
- Pytest, Postman/Newman and Locust test assets.

Deliberately mocked or out of scope:

- `mock-keyword-v1` uses category, location and keyword overlap; it is not
  SigLIP2 or a trained AI model.
- No RabbitMQ, transactional outbox, MinIO/S3, pgvector/Qdrant, moderation,
  notifications or production deployment.

## Project structure

```text
api_session_08_lost_found/
├── app.py
├── models.py
├── matching.py
├── tests/
├── postman/
├── scripts/
├── performance/
└── reports/
```

## Demo accounts

| Role in flow | Email | Password |
|---|---|---|
| Lost-item owner | `seeker@example.com` | `seeker123` |
| Found-item owner | `finder@example.com` | `finder123` |

These accounts and tokens are only for local coursework.

## Install and run

Use the shared SOA virtual environment:

```powershell
cd G:\SOA
.\.venv\Scripts\Activate.ps1
cd .\api_session_08_lost_found
python -m pip install -r requirements.txt
python -m app --port 5001
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/health
```

## Pytest

```powershell
python -m pytest -v
```

The tests cover authentication, schema validation, the Found Post image rule,
matching, claim creation and match limits.

## Postman and Newman

Import:

- `postman/lost-found.postman_collection.json`
- `postman/local.postman_environment.json`

Select the `Lost & Found Local` environment and run the collection in order.
The collection uses separate seeker/finder tokens and stores all generated IDs
as collection variables.

With the API running, execute:

```powershell
.\scripts\run-newman.ps1
```

JUnit output is written to `reports/newman-junit.xml`.

## Locust

Seed reproducible published data once before a load test:

```powershell
python -m scripts.seed_data
```

Scenario A:

```powershell
locust -f .\performance\locustfile.py --headless `
    -H http://127.0.0.1:5001 -u 10 -r 2 -t 30s `
    --html .\reports\A.html
```

Scenario B:

```powershell
locust -f .\performance\locustfile.py --headless `
    -H http://127.0.0.1:5001 -u 50 -r 5 -t 60s `
    --html .\reports\B.html
```

Scenario C:

```powershell
locust -f .\performance\locustfile.py --headless `
    -H http://127.0.0.1:5001 -u 200 -r 50 -t 30s `
    --html .\reports\C.html
```

The completed local results and proposed demo SLO are documented in
[`performance/analysis.md`](./performance/analysis.md). Detailed Locust reports
are available at `reports/A.html`, `reports/B.html` and `reports/C.html`.
