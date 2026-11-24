def v1_create_order(body):
    return {
        "api_version": "v1",
        "account_id": body["account_id"],
        "total": body.get("total", 0),
    }

def v2_create_order(body):
    return {
        "api_version": "v2",
        "account_id": body["account_id"],
        "amount": {
            "value": body.get("total", 0),
            "currency": body.get("currency", "VND"),
        },
        "status": "created",
    }