"""Load test the central Lost & Found matching endpoint.

Seed first: python -m scripts.seed_data
Run: locust -f performance/locustfile.py --headless \
         -H http://127.0.0.1:5001 -u 10 -r 2 -t 30s \
         --html reports/A.html
"""

import random

from locust import HttpUser, between, task
from locust.exception import StopUser


class LostFoundUser(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "seeker@example.com", "password": "seeker123"},
            name="SETUP POST /api/v1/auth/login",
        )
        if login.status_code != 200:
            raise StopUser()

        self.headers = {
            "Authorization": f"Bearer {login.json()['token']}"
        }
        posts = self.client.get(
            "/api/v1/posts",
            params={"type": "LOST", "status": "PUBLISHED"},
            headers=self.headers,
            name="SETUP GET /api/v1/posts",
        )
        if posts.status_code != 200:
            raise StopUser()

        self.lost_post_ids = [post["id"] for post in posts.json()["items"]]
        if not self.lost_post_ids:
            raise StopUser()

    @task
    def get_matches(self):
        post_id = random.choice(self.lost_post_ids)
        limit = random.choice((5, 10))
        with self.client.get(
            f"/api/v1/lost-posts/{post_id}/matches",
            params={"limit": limit},
            headers=self.headers,
            name="GET /api/v1/lost-posts/{id}/matches",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
                return

            body = response.json()
            if body.get("model_version") != "mock-keyword-v1":
                response.failure("Missing or unexpected model_version")
            elif not isinstance(body.get("items"), list):
                response.failure("items must be an array")
            elif body.get("count", 0) > limit:
                response.failure("Response exceeded requested limit")
            else:
                response.success()
