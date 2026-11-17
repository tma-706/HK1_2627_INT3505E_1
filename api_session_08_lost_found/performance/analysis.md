# Lost & Found Matching API — Load-test Analysis

## Scope and proposed SLO

Endpoint under test:

```http
GET /api/v1/lost-posts/{id}/matches?limit=5
```

Proposed demo SLO:

- Aggregated p95 response time below 300 ms.
- Real HTTP 5xx rate below 1%.
- Successful response rate at least 99%.

## Results

| Scenario | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A — baseline | 10 | 2 | 30s | | | |
| B — normal load | 50 | 5 | 60s | | | |
| C — spike | 200 | 50 | 30s | | | |

## Analysis

1. Which scenario has the highest p95, and where does latency start growing non-linearly?
2. Does RPS continue growing with users, or does it plateau?
3. Which scenarios meet the proposed SLO?
4. Which failures are real HTTP failures, validation failures, or client-side test failures?

## Limitations

This test exercises a deterministic keyword/category/location matching stub on
Flask's development server and SQLite. It does not measure SigLIP2 inference,
RabbitMQ, vector search, MinIO/S3, a production WSGI server, or a distributed
deployment. The proposed SLO is therefore a demo gate, not a production claim.
