import hashlib
import logging
from flask import request

from handlers import (
    v1_create_order,
    v2_create_order,
)

log = logging.getLogger("gateway")
# Thay đổi từ 5 đến 100 khi rollout.
V2_PERCENT = 5
V2_COHORTS = {
    "beta",
    "internal",
}
V2_FORCE_ACCOUNTS = {
    "acct_42",
    "acct_99",
}

def route_to_v2(body):
    # Ưu tiên 1: cohort được chỉ định bằng header.
    cohort = request.headers.get(
        "X-Cohort",
        "",
    ).lower()
    if cohort in V2_COHORTS:
        return True
        
    # Ưu tiên 2: account nằm trong allow-list.
    account_id = str(body.get("account_id", ""))
    if account_id in V2_FORCE_ACCOUNTS:
        return True

    # Ưu tiên 3: chia traffic theo hash bucket.
    if V2_PERCENT == 0:
        return False

    digest = hashlib.md5(
        account_id.encode("utf-8")
    ).hexdigest()
    bucket = int(digest, 16) % 100
    log.warning(
        "account=%s bucket=%s v2_percent=%s",
        account_id,
        bucket,
        V2_PERCENT,
    )
    return bucket < V2_PERCENT


def dispatch(body):
    if route_to_v2(body):
        return "v2", v2_create_order(body)
    return "v1", v1_create_order(body)