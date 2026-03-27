import os
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Optional fallback map for local demo only.
OPERATORS = {
    "giannis": {
        "full_name": "Γιάννης Παπαδόπουλος",
        "preferred_channel": "teams",
        "webhook_url": "https://default075e0cb3752a4320b3676d08b7918c.40.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/84b1fbab338349da97de6423eb8c5724/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=BnfIfL5urrw3vngHyYtssSf9YrnPFA-zxnCkIDruaoc",
        "phone_number": "+306997891734",
    }
}


def _normalize_operator(raw: Dict[str, Any], fallback_name: str) -> Optional[Dict[str, Any]]:
    """Maps external DB payload keys to the gateway operator contract."""
    if not raw:
        return None

    teams_webhook = raw.get("webhooks_url_teams") or raw.get("teams_webhook_url")
    slack_webhook = raw.get("webhooks_url_slack") or raw.get("slack_webhook_url")

    preferred_channel = (
        raw.get("preferred_channel")
        or raw.get("application")
        or raw.get("app")
        or raw.get("channel")
        or ("slack" if slack_webhook else "teams")
    )

    normalized = {
        "full_name": raw.get("name") or fallback_name,
        "preferred_channel": str(preferred_channel).lower(),
        "webhook_url": (
            raw.get("webhook_url")
            or raw.get("webhook")
            or teams_webhook
            or slack_webhook
        ),
        "phone_number": raw.get("phone"),
    }

    if not normalized["phone_number"] and not normalized["webhook_url"]:
        return None
    return normalized


def _fetch_operator_from_db(operator_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetches operator from MongoDB.
    Required env vars:
    - MONGODB_URI
    Optional env vars:
    - MONGODB_DB_NAME (default: hitl)
    - MONGODB_OPERATORS_COLLECTION (default: operators)
    """
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        return None

    db_name = os.getenv("MONGODB_DB_NAME", "hitl")
    collection_name = os.getenv("MONGODB_OPERATORS_COLLECTION", "operators")
    timeout_ms = int(float(os.getenv("OPERATORS_DB_TIMEOUT", "5")) * 1000)

    queries = [
        {"id": operator_name},
        {"operator_name": operator_name},
        {"username": operator_name},
        {"name": operator_name},
        {"id": {"$regex": f"^{operator_name}$", "$options": "i"}},
        {"name": {"$regex": f"^{operator_name}$", "$options": "i"}},
    ]

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        collection = client[db_name][collection_name]

        for query in queries:
            item = collection.find_one(query)
            if not item:
                continue
            normalized = _normalize_operator(item, operator_name)
            if normalized:
                client.close()
                return normalized
        client.close()
    except PyMongoError as exc:
        print(f"[USERS DB ERROR] Failed MongoDB lookup for '{operator_name}': {exc}")
    except Exception as exc:
        print(f"[USERS DB ERROR] Unexpected error during lookup for '{operator_name}': {exc}")

    return None


def get_operator(operator_name: str) -> Optional[Dict[str, Any]]:
    """Resolves operator data from MongoDB; optional local fallback for demos."""
    key = operator_name.lower().strip()
    from_db = _fetch_operator_from_db(key)
    if from_db:
        return from_db

    # Default is strict DB verification. Enable fallback only if explicitly requested.
    allow_fallback = os.getenv("ALLOW_LOCAL_OPERATOR_FALLBACK", "false").lower() == "true"
    if not allow_fallback:
        return None

    local = OPERATORS.get(key)
    if local:
        return _normalize_operator(local, key)
    return None