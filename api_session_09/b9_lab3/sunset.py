import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import jsonify, request
log = logging.getLogger("sunset")

def http_date(value):
    return format_datetime(value, usegmt=True)

def deprecate_at(sunset_date, replacement=None):
    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            now = datetime.now(timezone.utc)
            if now >= sunset_date:
                return jsonify({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement,
                }), 410
            result = function(*args, **kwargs)
            if isinstance(result, tuple):
                body, status = result
            else:
                body, status = result, 200
            response = jsonify(body)
            response.status_code = status
            response.headers["Sunset"] = http_date(
                sunset_date
            )
            response.headers["Deprecation"] = "true"
            if replacement:
                response.headers["Link"] = (
                    f'<{replacement}>; '
                    'rel="successor-version"'
                )
            log.warning(
                "deprecated_call path=%s remote=%s",
                request.path,
                request.remote_addr,
            )
            return response
        return wrapper
    return decorate