def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "service": "lost-found-api",
        "status": "ok",
    }


def test_auth_is_required(client, lost_payload):
    response = client.post("/api/v1/lost-posts", json=lost_payload)
    assert response.status_code == 401
    assert response.get_json()["code"] == "UNAUTHORIZED"


def test_lost_post_requires_description(client, seeker_headers, lost_payload):
    lost_payload["description"] = ""
    response = client.post(
        "/api/v1/lost-posts", json=lost_payload, headers=seeker_headers
    )
    assert response.status_code == 422
    body = response.get_json()
    assert body["code"] == "VALIDATION_ERROR"
    assert "description" in body["details"]


def test_found_post_requires_image_when_published(
    client, finder_headers, found_payload
):
    found_payload["image_urls"] = []
    created = client.post(
        "/api/v1/found-posts", json=found_payload, headers=finder_headers
    )
    assert created.status_code == 201

    response = client.post(
        f"/api/v1/posts/{created.get_json()['id']}/publish",
        headers=finder_headers,
    )
    assert response.status_code == 422
    assert response.get_json()["code"] == "IMAGE_REQUIRED"


def test_matching_and_claim_flow(
    client,
    seeker_headers,
    finder_headers,
    lost_payload,
    found_payload,
):
    lost = client.post(
        "/api/v1/lost-posts", json=lost_payload, headers=seeker_headers
    )
    assert lost.status_code == 201
    lost_id = lost.get_json()["id"]
    assert client.post(
        f"/api/v1/posts/{lost_id}/publish", headers=seeker_headers
    ).status_code == 200

    found = client.post(
        "/api/v1/found-posts", json=found_payload, headers=finder_headers
    )
    assert found.status_code == 201
    found_id = found.get_json()["id"]
    assert client.post(
        f"/api/v1/posts/{found_id}/publish", headers=finder_headers
    ).status_code == 200

    matches = client.get(
        f"/api/v1/lost-posts/{lost_id}/matches?limit=5",
        headers=seeker_headers,
    )
    assert matches.status_code == 200
    body = matches.get_json()
    assert body["model_version"] == "mock-keyword-v1"
    assert body["items"][0]["candidate_post_id"] == found_id
    assert body["items"][0]["rank"] == 1

    claim = client.post(
        f"/api/v1/found-posts/{found_id}/claims",
        headers=seeker_headers,
        json={
            "lost_post_id": lost_id,
            "evidence": "The inside pocket has my student card holder.",
        },
    )
    assert claim.status_code == 201
    assert claim.get_json()["status"] == "PENDING"


def test_match_limit_is_at_most_ten(
    client, seeker_headers, lost_payload
):
    lost = client.post(
        "/api/v1/lost-posts", json=lost_payload, headers=seeker_headers
    )
    lost_id = lost.get_json()["id"]
    client.post(f"/api/v1/posts/{lost_id}/publish", headers=seeker_headers)

    response = client.get(
        f"/api/v1/lost-posts/{lost_id}/matches?limit=11",
        headers=seeker_headers,
    )
    assert response.status_code == 422
    assert response.get_json()["code"] == "VALIDATION_ERROR"
